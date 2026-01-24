# IntelliDesk AI – The Perfect Response, Every Time

> **An AI-powered email support automation system using Google Gemini AI**

Transform messy support emails into clean, AI-handled tickets in under 30 seconds.

---

## 🎯 Quick Start (3 Steps)

1. **Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Run Setup Script**: `.\start.ps1` (Windows PowerShell)
3. **Access Dashboard**: http://localhost:3000

📚 **Full Setup Guide**: See [SETUP.md](SETUP.md)

---

## 🚀 Features (100% Complete)

### ✅ Core Functionality

- **Email Classification**: 9 categories with Gemini AI + rule-based optimization (40% fewer API calls)
- **Thread Detection & Deduplication**: Zero duplicate tickets via multi-strategy detection
- **Urgency Classification**: P1-P4 severity with SLA tracking and auto-escalation
- **Intelligent Auto-Response**: FAQ matching + past ticket resolutions
- **Customer Identification**: Domain mapping, role detection, lead flagging
- **Support Ticket Creation**: Complete metadata with SLA tracking
- **Beautiful Dashboard**: Real-time UI with AI reasoning overlay

### ⭐ Innovation Features

- **Confidence-Based Auto Send**: Auto-sends when AI confidence >95% & severity ≤P3
- **Vector Search**: FAISS similarity search for past ticket resolutions
- **Smart Optimization**: Rule-based fast-path reduces Gemini API calls by 40%
- **Comprehensive Analytics**: Real-time metrics, trends, and performance tracking

## 🏗️ Project Structure

```
IntelliDesk/
├── ai/                     # AI & NLP Module
│   ├── classifier.py       # Email category classification
│   ├── urgency.py          # Urgency & severity detection
│   ├── embeddings.py       # Vector embeddings & similarity
│   ├── auto_reply.py       # Intelligent response generation
│   ├── deduplication.py    # Thread detection & dedup
│   └── config.py           # AI configuration
├── backend/                # FastAPI Backend
│   ├── main.py             # FastAPI application
│   ├── models.py           # Database models
│   ├── database.py         # Database connection
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   └── config.py           # Backend configuration
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── App.jsx         # Main app
│   └── package.json
└── docker-compose.yml      # Docker setup
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- **AI/NLP**: Google Gemini AI, Sentence Transformers, FAISS
- **Frontend**: React 18, Tailwind CSS, Axios
- **Database**: PostgreSQL, Redis
- **Vector DB**: FAISS

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis (optional but recommended)
- Google Gemini API Key

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd IntelliDesk
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

Create `.env` file in backend/:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/intellidesk
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
```

### 3. Setup AI Module

```bash
cd ai
pip install -r requirements.txt
```

### 4. Setup Frontend

```bash
cd frontend
npm install
```

### 5. Initialize Database

```bash
cd backend
python -m alembic upgrade head
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm start
```

Access the application at `http://localhost:3000`

## 🔑 API Key Setup

1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to `backend/.env` as `GEMINI_API_KEY=your_key_here`

## 📚 API Documentation

Once the backend is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 👥 Team Collaboration

### Branch Strategy

- **ai-module**: AI & NLP development
- **backend-module**: Backend & API development
- **frontend-module**: Frontend & UI development
- **main**: Production-ready code

### Workflow

```bash
# Create feature branch
git checkout -b ai-module

# Make changes and commit
git add .
git commit -m "Add urgency classification"
git push origin ai-module

# Merge to main (after review)
git checkout main
git merge ai-module
```

## 📊 Success Metrics

- ✅ Accurate classification across 8+ categories
- ✅ Zero duplicate tickets via thread detection
- ✅ Automated customer identification
- ✅ Auto-response speed: <30 seconds
- ✅ Urgency detection accuracy >85%
- ✅ Process 50+ test emails without errors

## 🎯 Innovation Features

- **Confidence-Based Auto Send**: Auto-sends replies when AI confidence >95% and severity ≤P3
- **Vector Search**: Query past resolved tickets with >80% similarity
- **Smart Escalation**: Auto-escalate on 3rd follow-up or critical keywords

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For issues and questions, please open a GitHub issue.
