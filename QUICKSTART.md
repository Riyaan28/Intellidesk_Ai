# 🚀 IntelliDesk AI - Quick Reference Card

## ⚡ 5-Minute Setup

```powershell
# 1. Get Gemini API Key
# Visit: https://makersuite.google.com/app/apikey

# 2. Run Quick Start
.\start.ps1

# 3. Access Application
# Dashboard: http://localhost:3000
# API Docs:  http://localhost:8000/docs
```

---

## 📋 Essential Commands

### Start Application

```powershell
.\start.ps1          # Quick start (opens both backend & frontend)
```

### Manual Start

```powershell
# Backend
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm run dev
```

### Stop Application

```powershell
# Press Ctrl+C in each terminal window
```

---

## 🧪 Quick Test

### Test Email Processing

1. Go to: http://localhost:8000/docs
2. Find: `/api/test-email` endpoint
3. Click: "Try it out" → "Execute"
4. Result: See ticket created with AI classification

### View in Dashboard

1. Go to: http://localhost:3000
2. See: Ticket appears in dashboard
3. Click: On ticket for full details
4. View: AI reasoning, response, and SLA

---

## 📁 Project Structure

```
IntelliDesk/
├── ai/              → AI & NLP (Gemini integration)
├── backend/         → FastAPI server
├── frontend/        → React dashboard
├── README.md        → Start here
├── SETUP.md         → Detailed setup
├── API.md           → API documentation
├── TESTING.md       → Test samples
└── start.ps1        → Quick start script
```

---

## 🔑 Configuration

### Add Gemini API Key

```powershell
# Edit: backend\.env
GEMINI_API_KEY=your_actual_api_key_here
```

### Database Options

```powershell
# PostgreSQL (Recommended)
DATABASE_URL=postgresql://intellidesk:intellidesk123@localhost:5432/intellidesk

# SQLite (Quick Test)
DATABASE_URL=sqlite:///./intellidesk.db
```

---

## 🎯 Key URLs

| Service    | URL                                  | Description   |
| ---------- | ------------------------------------ | ------------- |
| Dashboard  | http://localhost:3000                | Main UI       |
| API Docs   | http://localhost:8000/docs           | Swagger UI    |
| Health     | http://localhost:8000/health         | System status |
| Test Email | http://localhost:8000/api/test-email | Quick test    |

---

## 📊 Sample Email for Testing

```json
{
  "subject": "URGENT: App crashes when uploading files",
  "body": "Hi Support,\n\nOur app crashes when users upload PDF files >10MB.\n\nThis is affecting ALL USERS!\n\nPlease help ASAP!\n\nJohn Smith\nIT Manager\njohn@techcorp.com",
  "sender": "john.smith@techcorp.com"
}
```

**Expected Result:**

- Category: Technical Support
- Severity: P1 (Critical)
- SLA: 1 hour
- Auto-response generated

---

## 🛠️ Troubleshooting

### "Module not found"

```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### "Database error"

```powershell
# Switch to SQLite in backend\.env
DATABASE_URL=sqlite:///./intellidesk.db
```

### "Gemini API error"

```powershell
# Verify API key in backend\.env
# Check: https://makersuite.google.com/app/apikey
```

### "Frontend won't start"

```powershell
cd frontend
npm install
npm run dev
```

---

## 📚 Documentation Files

| File                   | Purpose                 |
| ---------------------- | ----------------------- |
| **README.md**          | Project overview        |
| **SETUP.md**           | Complete setup guide    |
| **API.md**             | API endpoint docs       |
| **TESTING.md**         | Test samples            |
| **TEAM.md**            | Team collaboration      |
| **PROJECT_SUMMARY.md** | Full project summary    |
| **CHECKLIST.md**       | Completion verification |

---

## ✅ Success Checklist

- [ ] Gemini API key added to `.env`
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Test email endpoint works
- [ ] Dashboard displays tickets
- [ ] Can click on ticket for details
- [ ] AI classification visible
- [ ] SLA countdown showing

---

## 🎯 Key Features to Demo

1. **Email Classification**: See AI categorize emails with confidence
2. **Urgency Detection**: Watch P1-P4 severity assignment
3. **Auto-Response**: View AI-generated responses
4. **Deduplication**: Test thread detection
5. **Customer ID**: See domain mapping work
6. **Dashboard**: Explore real-time analytics
7. **Response Preview**: Side-by-side email vs AI response

---

## 💡 Quick Tips

- **Port already in use?** Change port in `backend/main.py` or `frontend/vite.config.js`
- **Slow AI responses?** Check your internet connection (API calls)
- **Want to reset?** Delete `backend/intellidesk.db` and restart
- **Need more test data?** Use batch processing endpoint with multiple emails

---

## 🚀 Team Workflow

```powershell
# Member 1: AI Module
git checkout -b ai-module
# Work on ai/ folder

# Member 2: Backend
git checkout -b backend-module
# Work on backend/ folder

# Member 3: Frontend
git checkout -b frontend-module
# Work on frontend/ folder

# Merge when ready
git checkout main
git merge <branch-name>
```

---

## 📞 Support Resources

- **Setup Issues**: Check SETUP.md
- **API Questions**: Check API.md
- **Testing**: Check TESTING.md
- **Team Collaboration**: Check TEAM.md
- **Complete Overview**: Check PROJECT_SUMMARY.md

---

## 🎉 What You Built

✅ AI-powered email support system
✅ Automatic classification (9 categories)
✅ Smart deduplication (zero duplicates)
✅ Intelligent auto-responses
✅ Beautiful dashboard UI
✅ Real-time SLA tracking
✅ Customer identification
✅ Vector similarity search

**Powered by Google Gemini AI** 🤖

---

## 🔗 Important Links

- **Gemini API**: https://makersuite.google.com/app/apikey
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com

---

**Last Updated**: January 2026
**Status**: ✅ Production Ready
**Made with**: Google Gemini AI

---

**Quick Start Command**: `.\start.ps1` 🚀
