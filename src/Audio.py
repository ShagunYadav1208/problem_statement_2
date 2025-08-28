import queue
import sys
import sounddevice as sd
import numpy as np
import json
import os
from datetime import datetime
from faster_whisper import WhisperModel
from transformers import pipeline
import re

# 🎙️ Config
MODEL_SIZE = "small"
DEVICE = "cuda"
DTYPE = "float32"
SAMPLE_RATE = 16000
BLOCK_SIZE = 6000

print("🧠 Loading model...")
model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=DTYPE)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
print("✅ Model ready")

# Files
TRANSCRIPT_FILE = "transcripts.json"
SUMMARY_FILE = "summarizeSpeech.json"

# Reset transcripts.json on every run
with open(TRANSCRIPT_FILE, "w") as f:
    json.dump({"transcripts": []}, f)

# Ensure summary file exists
if not os.path.exists(SUMMARY_FILE):
    with open(SUMMARY_FILE, "w") as f:
        json.dump({"summaries": []}, f)

with open(TRANSCRIPT_FILE, "w") as f:
    json.dump({"transcripts": []}, f)

def save_transcript(text):
    with open(TRANSCRIPT_FILE, "r+") as f:
        data = json.load(f)
        data["transcripts"].append({"text": text})
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

def load_transcripts():
    with open(TRANSCRIPT_FILE, "r") as f:
        return json.load(f)["transcripts"]

def summarize_session():
    transcripts = load_transcripts()
    full_text = " ".join([t["text"] for t in transcripts])

    if not full_text.strip():
        print("⚠️ Nothing to summarize")
        return

    # Generate summary (dynamic max_length based on input)
    input_len = len(full_text.split())
    max_len = min(300, input_len // 2 + 50)
    min_len = min(100, max(30, input_len // 5))

    summary = summarizer(
        full_text, max_length=max_len, min_length=min_len, do_sample=False,
        clean_up_tokenization_spaces=True
    )[0]["summary_text"]

    # Extract key points
    key_points = [s.strip() for s in re.split(r"[.?!]", summary) if s.strip()]

    result = {
        "summary": summary,
        "key_points": key_points,
    }

    # Always overwrite summarizeSpeech.json with fresh structure
    if not os.path.exists("summarizeSpeech.json"):
        with open("summarizeSpeech.json", "w") as f:
            json.dump({"summaries": []}, f)

    with open("summarizeSpeech.json", "r+") as f:
        data = json.load(f)
        if "summaries" not in data:
            data["summaries"] = []
        data["summaries"].append(result)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    print("\n📖 Summarizing entire session...")
    print("✅ Saved summary to summarizeSpeech.json")
    print("📌 Summary:", summary)
    print("👉 Key Points:", key_points)

def audio_callback(indata, frames, time, status):
    if status:
        print("⚠️", status, file=sys.stderr)
    audio_q.put(indata.copy())

# Audio queue
audio_q = queue.Queue()

def listen_and_transcribe():
    buffer = np.zeros(0, dtype=np.float32)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback,
        blocksize=BLOCK_SIZE,
    ):
        print("🎤 Speak... (say 'summarize' to stop and summarize)")
        while True:
            block = audio_q.get().flatten()
            buffer = np.concatenate((buffer, block))

            if len(buffer) > SAMPLE_RATE * 2:
                segments, _ = model.transcribe(buffer, language="en", vad_filter=True)
                text = " ".join([seg.text for seg in segments]).strip()

                if text:
                    print("📝", text)
                    save_transcript(text)

                    if "summarize" in text.lower():
                        summarize_session()
                        break

                buffer = np.zeros(0, dtype=np.float32)

if __name__ == "__main__":
    try:
        listen_and_transcribe()
    except KeyboardInterrupt:
        print("\n👋 Stopped")