# 🤖 Datasmith AI

**Datasmith** is a production-ready, full-stack AI application designed for advanced document analysis and code inspection. It combines a modern, responsive React frontend with a robust FastAPI backend to provide seamless interaction with Google's Gemini models.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E75B2?logo=google&logoColor=white)

## ✨ Features

### 🧠 Intelligent Analysis
- **Multi-Modal Support:** Analyze text, code, PDFs, images (OCR), audio files, and YouTube videos.
- **Smart Agents:**
  - **Code Analysis:** Detect bugs, explain logic, and estimate time/space complexity.
  - **Summarization:** Generate structured summaries or TL;DRs.
  - **General Chat:** Context-aware conversations.

### 💻 Modern Frontend
- **Interactive Chat UI:** Clean interface with markdown support and syntax highlighting.
- **Voice Input:** Real-time speech-to-text for hands-free interaction.
- **File Management:** Drag-and-drop file uploads with preview.
- **Audio Playback:** Text-to-speech playback for AI responses.
- **Slash Commands:** Quick access to tools like `/code_analysis` and `/summarize`.

### ⚙️ Robust Backend
- **Clean Architecture:** Domain-driven design separating logic, infrastructure, and API layers.
- **Structured Outputs:** Uses Pydantic for consistent and type-safe AI responses.
- **Extensible Extractors:** Modular design for adding new data sources.
- **Observability:** Token usage tracking and cost estimation.

## 🔄 Workflow

![AI Agent Extraction Flow](./AI%20Agent%20Extraction%20Flow-2026-02-07-231405.png)

## 🛠️ Tech Stack

**Frontend:**
- **Framework:** React 19 (Vite)
- **Styling:** CSS Modules, Lucide React Icons
- **Markdown:** React Markdown + Remark GFM
- **Syntax Highlighting:** React Syntax Highlighter (Prism)

**Backend:**
- **API:** FastAPI + Uvicorn
- **AI Orchestration:** LangChain
- **Models:** Google Gemini (via `google-genai`)
- **Audio:** Deepgram SDK
- **Data extraction:** `pypdf2`, `youtube-transcript-api`, `pillow`

**Infrastructure:**
- **Containerization:** Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- API Keys:
  - **Google Gemini API Key** (for LLM)
  - **Deepgram API Key** (for Audio/Voice)

### ⚡ Quick Start (Docker)

The easiest way to run Datasmith is using Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/datasmith.git
    cd datasmith
    ```

2.  **Configure Environment:**
    Create a `.env` file in the `backend/` directory:
    ```bash
    cp backend/.env.example backend/.env
    ```
    Edit `backend/.env` and add your keys:
    ```env
    GOOGLE_API_KEY=your_google_key_here
    DEEPGRAM_API_KEY=your_deepgram_key_here
    ENVIRONMENT=development
    LLM_MODEL=gemini-2.0-flash-exp
    ```

3.  **Run the App:**
    ```bash
    docker compose up --build
    ```

4.  **Access:**
    - **Frontend:** http://localhost:5173 (or port defined in compose)
    - **Backend API:** http://localhost:8000
    - **API Docs:** http://localhost:8000/docs

---

### 🔧 Manual Setup (Development)

#### Backend

1.  Navigate to `backend`:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set environment variables (or use `.env`):
    ```bash
    export GOOGLE_API_KEY=your_key
    export DEEPGRAM_API_KEY=your_key
    ```
4.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```

#### Frontend

1.  Navigate to `frontend`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the dev server:
    ```bash
    npm run dev
    ```

## 📖 Usage Guide

### Chat Interface
- Type naturally to chat with the AI.
- Use **Slash Commands** for specific tasks:
  - `/code_analysis` - Paste code or attach a file to get a bug report and complexity analysis.
  - `/summarize` - Get a detailed summary of attached documents or text.
  - `/tldr` - Quick bullet-point summary.

### File Analysis
- **Drag & Drop** files (PDF, Images, Audio) directly into the chat window.
- The AI will automatically extract text/content and use it as context for your query.

### YouTube Analysis
- Paste a YouTube URL.
- The backend extracts the transcript (if available) and allows you to ask questions about the video content.

## 📂 Project Structure

```
datasmith/
├── backend/                # Python FastAPI Backend
│   ├── api/                # API Routes & Middleware
│   ├── core/               # Business Logic & AI Agents
│   │   ├── agents/         # Summarize, Code Analysis, etc.
│   │   └── extractors/     # PDF, Image, YouTube, Audio logic
│   ├── infrastructure/     # LLM Clients & Config
│   ├── uploads/            # Temp storage for file processing
│   └── main.py             # App Entrypoint
├── frontend/               # React Vite Frontend
│   ├── src/
│   │   ├── components/     # Chat, UI, & Audio components
│   │   ├── services/       # API integration
│   │   └── App.jsx         # Main App Wrapper
│   └── package.json
└── docker-compose.yml      # Orchestration
```
