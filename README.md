# 🤖 AI Agent Orchestration Platform

![LangGraph](https://img.shields.io/badge/LangGraph-Framework-blue) ![LangChain](https://img.shields.io/badge/LangChain-Integration-green) ![Streamlit](https://img.shields.io/badge/Streamlit-UI-red) ![Flask](https://img.shields.io/badge/Flask-API-black) ![Twilio](https://img.shields.io/badge/Twilio-Voice/SMS-red)

> A modular, tool-augmented AI orchestration platform for sophisticated hospitality-focused conversations. Built with LangGraph, it supports rich interactions across web, WhatsApp, and voice.

The project centralizes all orchestration logic in the **hospitalitybot** agent, replacing the previous multi-agent structure. It enables seamless communication using text and voice, powered by **intent-based routing**, **multi-modal tools**, and **long-term memory**.

---

## ✨ Key Features

*   🧠 **Multi-Agent Orchestration:** Utilizes **LangGraph** to create stateful, multi-agent graphs, allowing for complex and flexible conversational flows.
*   🔀 **Intent-Based Routing:** A central router intelligently directs user queries to the most appropriate agent or tool based on intent.
*   🛠️ **Tool-Augmented Agents:** Agents are equipped with a variety of tools, such as flight status checkers, booking APIs, and FAQ retrieval systems, to perform real-world actions.
*   🔄 **Multi-LLM Support:** Seamlessly switch between major LLM providers like **Google Gemini**, **OpenAI**, and **Anthropic Claude** via environment variables.
*   🗣️ **Multimodal Interfaces:**
    *   **Web:** Interactive chat UI built with **Streamlit**.
    *   **Mobile:** **Twilio WhatsApp bot** for text-based conversations.
    *   **Voice Chat:** Offline speech support using Whisper + Piper
*   💾 **Hybrid Memory System:** Combines a sliding window for short-term context with a **FAISS vector store** for long-term memory recall, ensuring conversations are both coherent and personalized.
*   📊 **Observability with Langfuse:** Deep integration with Langfuse for tracing, debugging, and analyzing agent performance, latency, and token usage.

---

## 🏗️ Architecture

At the heart of the platform is the `hospitalitybot/` folder, which defines the main LangGraph-based conversational agent and its routing, tools, and memory setup.

![Architecture Diagram](assets/architecture-diagram.png "High-level architecture of the agent orchestration platform.")

---

## 📂 Project Structure

The repository is organized to separate concerns, making it easy to extend and maintain.

```
ai_hackathon/
├── hospitalitybot/      # Core LangGraph logic (agent, state, routers, nodes)
│   ├── graph.py
│   ├── state.py
│   ├── nodes.py
│   ├── routers.py
├── apps/                # Entry points for Streamlit, Flask, Twilio
│   ├── streamlit_app.py # Streamlit app
│   ├── twilio_app.py    # WhatsApp webhook
│   └── dashboard.py     # Langfuse trace viewer
├── config/              # Prompt files and environment config
│   └── prompts/
├── workflows/           # Base agent setup, routers, aggregation
├── tools/               # Tool functions (flight check, booking, FAQ)
├── utils/               # Memory setup, STT/TTS wrapper, etc.
├── models/              # Offline Whisper/Piper models
│   ├── stt/             # Whisper model files
│   └── tts/             # Piper voice files
├── data/                # Mock data (e.g. FAQs)
├── .env.example         # Environment variable sample
├── requirements.txt
└── test_graph.py        # CLI tester
```

---

## ⚙️ Setup Instructions

### 1. Clone and Setup

```bash
git clone https://github.com/chiraaag004/AI-Agent-Orchestrator
cd ai_hackathon
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Whisper + FFmpeg

```bash
# Linux
sudo apt install ffmpeg
# macOS
brew install ffmpeg
```

### 3. Download Offline Models

* Whisper model (e.g., `small.en.pt`) → `models/stt/`
* Piper model (e.g., `en_US-lessac-medium.onnx`) → `models/tts/`

### 4. Set up .env

```bash
cp .env.example .env
```

Fill in:

* `LLM_PROVIDER`, `MODEL_NAME`
* `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
* `GOOGLE_API_KEY`, `OPENAI_API_KEY`, etc.
* `WHISPER_MODEL_NAME`, `PIPER_VOICE_MODEL_PATH`
* `LANGFUSE_SECRET_KEY` (optional)

---

## 🌟 Running Applications

### 🔗 Web Chat Interface (Hospitality Bot)

```bash
streamlit run apps/streamlit_app.py
```

### 📲 WhatsApp Integration

```bash
python apps/twilio_app.py
```

Set webhook in Twilio sandbox.

### 📊 Admin Dashboard

```bash
streamlit run apps/dashboard.py
```

### 🔍 Command-Line Test

```bash
python test_graph.py
```

---

## 🧠 Memory System

* **Short-Term:** Sliding window of N messages (configurable).
* **Long-Term:** Uses FAISS vector store to retrieve relevant past information (preferences, bookings).

---

## 📊 Observability

* Built-in Langfuse integration.
* Streamlit dashboard to visualize LangGraph traces.
* Track agent paths, latencies, errors, and token costs.

---

## 🔊 Voice Processing

* **STT (Speech-to-Text):** Whisper (offline)
* **TTS (Text-to-Speech):** Piper (offline)
* **Utils:** `utils/voice_services.py`

---

## 📖 Configuration Overview (.env)

```ini
LLM_PROVIDER=gemini
MODEL_NAME=gemini-pro
WHISPER_MODEL_NAME=small.en
PIPER_VOICE_MODEL_PATH=models/tts/en_US-lessac-medium.onnx
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=whatsapp:+1234567890
CONFIDENCE_THRESHOLD=0.6
CONVERSATION_WINDOW_SIZE=4
LANGFUSE_SECRET_KEY=...
```

---

## 🚀 Extending the Platform

* Add new agents under `agents/<agent_name>`
* Define new tools in `tools/`
* Add routing rules via `router.py`
* Add new prompts under `config/prompts/`
* Reuse memory, translation, and observability layers

---