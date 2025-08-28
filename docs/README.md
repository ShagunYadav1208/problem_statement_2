# 🤖 Smart Personal Assistant

A Python-based **AI Personal Assistant** that merges **Audio AI, Vision AI, and a Tkinter Desktop App** into a unified, offline-capable system. It offers **privacy, reliability, and unique multimodal features** by avoiding reliance on cloud-only services.

---

## 🚀 Key Features

### 📞 Contact Management
- Add new contacts  
- Delete existing contacts  
- Simulate calls  

### 💾 File Management
- Save notes and speech/text inputs directly to local files  

### 🎤 Speech Features
- Speech-to-text (Whisper)  
- Text-to-speech (gTTS)  
- Pronunciation practice  
- Grammar correction  

### 🎨 Modern UI
- Built with **Tkinter & CustomTkinter**  
- Clean, modern layout with progress bars and clear button design  

### 🎙️ Audio Assistant
- Real-time transcription with **Whisper**  
- Summarization with **BART**  
- Generates key points from conversations  

### 👀 Vision Assistant
- Object detection using **YOLOv8**  
- Image captioning with **BLIP**  
- Stores visual history with timestamps  
- Scene summarization with **GPT2**  

### 📖 Memory System
- Stores and manages both **speech** and **vision events** in JSON files  
- Supports recall, summarization, and deletion of past events  

---

## 🧠 Models Used
- **Whisper** → Speech-to-Text  
- **BART** → Summarization  
- **YOLOv8** → Object Detection  
- **BLIP** → Image Captioning  
- **GPT2** → Text Generation  

---

## 🛠️ How It Works

### 🔊 Audio Flow
1. Captures microphone input  
2. Transcribes with Whisper  
3. Saves transcript to memory  
4. Generates summaries & key points on request  

### 👁️ Vision Flow
1. Captures webcam frames  
2. Detects objects (YOLOv8)  
3. Generates captions (BLIP)  
4. Stores + timestamps visual memory  
5. Expands into detailed scenes (GPT2)  

### 🧾 Memory Flow
- Logs all **speech & vision events** into JSON files  
- Supports recall, summarization, and deletion  

### 🖥️ Tkinter Productivity Flow
- Central hub for **contacts, notes, and language practice**  
- Integrates speech-to-text and text-to-speech seamlessly  

---

## 📂 File Outputs

- `transcripts.json` → Raw speech transcripts  
- `summarizeSpeech.json` → Summaries of speech sessions  
- `vision_transcripts.json` → Frame-by-frame image captions  
- `vision_summary.json` → Summaries of visual events  
- `memory.json` → Unified log of all events  

---

## 🚀 Why It's Unique

- **Offline Functionality** → Works without cloud APIs, ensuring privacy  
- **Multimodal Integration** → Speech + Vision + Productivity in one app  
- **Structured Memory** → Organized, recallable context  
- **Flexible Interfaces** → GUI  

---

## 🔮 Future Scope

- 📊 Full GUI Integration (unified Tkinter dashboard)  
- 📱 Mobile App Conversion (cross-platform)  
- 🖥️ Multimodal Dashboard (real-time transcripts + captions)   
- 🕸️ Knowledge Graph Memory (queryable event storage)  
- 🎥 Voice + Vision Fusion   

---

## 🛠️ Tech Stack

- **Language:** Python 3.x  
- **Libraries:** Torch, Transformers, HuggingFace, Pandas, OpenCV, SoundDevice, Numpy  
- **Core Models:** Faster-Whisper, YOLOv8, BLIP, GPT2, BART  
- **GUI:** Tkinter & CustomTkinter  
- **Text-to-Speech:** gTTS  

---

## 🎯 Conclusion

This project demonstrates a **self-contained AI Personal Assistant** that integrates **speech recognition, vision understanding, and memory summarization** with a **desktop productivity GUI**.  

Unlike cloud-based assistants, it runs **offline**, prioritizing **privacy, reliability, and user control**, making it a **powerful alternative** for personal productivity and AI integration.  

---

