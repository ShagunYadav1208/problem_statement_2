import os
import cv2
import json
import re
import threading
import queue
from datetime import datetime
from collections import deque

import torch
import numpy as np
import face_recognition
from ultralytics import YOLO
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    pipeline,
    AutoModelForCausalLM,
    AutoTokenizer
)

# =========================================================
# Device
# =========================================================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Using device: {device}")

# =========================================================
# Text summarizer
# =========================================================
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# =========================================================
# Scene generator (text-generation model)
# =========================================================
scene_model_name = "gpt2"  # swap with Falcon/Mistral for stronger outputs
tokenizer = AutoTokenizer.from_pretrained(scene_model_name)
scene_model = AutoModelForCausalLM.from_pretrained(scene_model_name).to(device)
scene_generator = pipeline(
    "text-generation",
    model=scene_model,
    tokenizer=tokenizer,
    device=0 if device == "cuda" else -1
)

# =========================================================
# Vision models
# =========================================================
yolo_model = YOLO("yolov8n.pt").to(device)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

# =========================================================
# Frame Handling
# =========================================================
frame_queue = queue.Queue(maxsize=5)
latest_frame = None
frame_lock = threading.Lock()

# =========================================================
# Memory
# =========================================================
event_memory = deque(maxlen=100)
MEMORY_FILE = "memory.json"

VISION_TRANSCRIPT_FILE = "vision_transcripts.json"
VISION_SUMMARY_FILE = "vision_summary.json"

# Reset transcript file each run
with open(VISION_TRANSCRIPT_FILE, "w") as f:
    json.dump({"captions": []}, f)

# Ensure summary file exists
if not os.path.exists(VISION_SUMMARY_FILE):
    with open(VISION_SUMMARY_FILE, "w") as f:
        json.dump({"summaries": []}, f)

# =========================================================
# Memory functions
# =========================================================
def remember_event(event: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_memory.append({"time": timestamp, "event": event})


def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(list(event_memory), f, indent=2)


def load_memory():
    global event_memory
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            event_memory = deque(data, maxlen=100)


def summarize_memory():
    if not event_memory:
        return "I don’t remember anything yet."
    text = " ".join(e["event"] for e in event_memory)
    summary = summarizer(
        text,
        max_length=150,
        min_length=50,
        do_sample=False,
        truncation=True
    )[0]["summary_text"]
    return summary

# =========================================================
# Vision transcript functions
# =========================================================
def save_caption(caption: str):
    with open(VISION_TRANSCRIPT_FILE, "r+") as f:
        data = json.load(f)
        data["captions"].append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "caption": caption
        })
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


def load_captions():
    with open(VISION_TRANSCRIPT_FILE, "r") as f:
        return json.load(f)["captions"]


def summarize_captions():
    captions = load_captions()
    full_text = " ".join([c["caption"] for c in captions])

    if not full_text.strip():
        return "⚠️ Nothing to summarize"

    input_len = len(full_text.split())
    max_len = min(300, input_len // 2 + 50)
    min_len = min(100, max(30, input_len // 5))

    summary = summarizer(
        full_text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        truncation=True
    )[0]["summary_text"]

    key_points = [s.strip() for s in re.split(r"[.?!]", summary) if s.strip()]

    result = {
        "summary": summary,
        "key_points": key_points,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(VISION_SUMMARY_FILE, "r+") as f:
        data = json.load(f)
        if "summaries" not in data:
            data["summaries"] = []
        data["summaries"].append(result)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    return summary

# =========================================================
# Scene Expansion
# =========================================================
def expand_to_scene(summary: str) -> str:
    # Remove repeated words like "self self self"
    summary = re.sub(r"\b(\w+)( \1\b)+", r"\1", summary)

    prompt = (
        "You are a storyteller AI. Expand the following vision summary into a vivid natural "
        "scene, explaining what is happening in human terms:\n\n"
        f"Vision Summary: {summary}\n\n"
        "Scene:"
    )

    output = scene_generator(
        prompt,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        truncation=True,
        pad_token_id=tokenizer.eos_token_id
    )

    scene_text = output[0]["generated_text"].split("Scene:", 1)[-1].strip()
    return scene_text

# =========================================================
# Vision Processing
# =========================================================
def generate_caption(frame):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    inputs = blip_processor(image, return_tensors="pt").to(device)
    out = blip_model.generate(**inputs)
    caption = blip_processor.decode(out[0], skip_special_tokens=True)
    return caption


def is_meaningful_change(new_caption, last_caption):
    return new_caption != last_caption


def process_frames():
    global latest_frame
    last_caption = ""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            caption = generate_caption(frame)

            if is_meaningful_change(caption, last_caption):
                print(f"[Vision]: {caption}")
                remember_event(caption)
                save_caption(caption)
                last_caption = caption


def capture_frames():
    global latest_frame
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        with frame_lock:
            latest_frame = frame.copy()

        if not frame_queue.full():
            frame_queue.put(frame.copy())

# =========================================================
# Assistant
# =========================================================
def assistant():
    print("🤖 AI Companion Started. Type 'quit' to exit.")
    while True:
        cmd = input("👉 You: ")

        if cmd.lower() == "quit":
            save_memory()
            break
        elif cmd.lower() == "recall":
            print("📖", summarize_memory())
        elif cmd.lower() == "forget":
            event_memory.clear()
            save_memory()
            print("🗑️ I have forgotten everything.")
        elif cmd.lower() == "summarize":
            summary = summarize_captions()
            print("📌 Vision Summary:", summary)

            scene_desc = expand_to_scene(summary)
            print("🎬 Scene Description:", scene_desc)
        else:
            print(f"🗣️ You said: {cmd}")

# =========================================================
# Main
# =========================================================
if __name__ == "__main__":
    load_memory()
    threading.Thread(target=capture_frames, daemon=True).start()
    threading.Thread(target=process_frames, daemon=True).start()
    assistant()