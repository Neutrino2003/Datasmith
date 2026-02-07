# 🤖 Datasmith AI - Production-Ready API

AI-powered document analysis with **FastAPI REST API** and clean architecture.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## ✨ Features

- **📄 Document Processing** - PDF, Images (OCR), Audio, YouTube
- **🤖 AI Analysis** - Summarization, Code Analysis, General Chat
- **🔌 REST API** - Full OpenAPI documentation
- **📊 Token Tracking** - Real-time cost estimation
- **☁️ Cloud-Ready** - Deploy to Railway, Render, Fly.io, Cloud Run

## 🏗️ Architecture

```
backend/
├── api/v1/routes/      # FastAPI endpoints
├── core/               # Domain logic
│   ├── agents/        # AI agents (coordinator, summarize, code analysis)
│   └── extractors/    # Content extraction (PDF, image, audio, YouTube)
├── infrastructure/     # External services
│   ├── llm/           # LLM client factory, pricing, stats
│   └── config.py      # Settings management
└── utils/             # Shared utilities
```

**Clean Code Principles:**
- PEP-8 compliant
- No unnecessary comments
- Shared LLM client (DRY)
- Full type hints
- Async-first

## 🚀 Quick Start

### Using Docker

```bash
# Setup environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start the API
docker compose up --build

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Local Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your_key
export DEEPGRAM_API_KEY=your_key

# Run the API
uvicorn main:app --reload
```

## 📡 API Endpoints

### Analysis

```bash
# Analyze text
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here", "session_id": "session1"}'

# Analyze file
curl -X POST http://localhost:8000/api/v1/analyze/file \
  -F "file=@document.pdf" \
  -F "session_id=session1"
```

### Extraction

```bash
# Extract from PDF
curl -X POST http://localhost:8000/api/v1/extract/pdf \
  -F "file=@document.pdf"

# Extract from YouTube
curl -X POST http://localhost:8000/api/v1/extract/youtube \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=..."}'
```

### Health

```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/health/ready
```

## ⚙️ Configuration

Environment variables in `.env`:

```env
GOOGLE_API_KEY=your_google_api_key
DEEPGRAM_API_KEY=your_deepgram_key

ENVIRONMENT=development
LLM_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.3
MAX_TOKENS=8192

CORS_ORIGINS=*
```

## 📊 Supported Models

| Model | Use Case | Cost (per 1M tokens) |
|-------|----------|---------------------|
| `gemini-2.0-flash-exp` | Default, fast | $0.10 / $0.40 |
| `gemini-1.5-flash` | Production | $0.075 / $0.30 |
| `gemini-1.5-pro` | Complex tasks | $1.25 / $5.00 |

## 🔌 API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ☁️ Deployment

### Railway

```bash
railway up
```

### Render

```bash
render deploy
```

### Fly.io

```bash
fly deploy
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Test analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test summarization", "session_id": "test"}'
```

## 📝 Project Structure

- **Clean Architecture** - Domain/Infrastructure/Presentation layers
- **PEP-8 Compliant** - Professional Python style
- **Type Safe** - Full type hints throughout
- **DRY** - Shared LLM client, no duplication
- **Async-First** - Non-blocking I/O

## 📄 License

MIT License

---

**Production-Ready Backend** - Deploy anywhere, integrate with any frontend
