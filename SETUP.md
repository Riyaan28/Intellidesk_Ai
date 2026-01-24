# IntelliDesk AI - Setup Guide

## Quick Start (5 Minutes)

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

### 2. Setup Backend

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Setup Database

**Option A: PostgreSQL (Recommended)**

```powershell
# Install PostgreSQL if needed
# Then create database:
psql -U postgres
CREATE DATABASE intellidesk;
CREATE USER intellidesk WITH PASSWORD 'intellidesk123';
GRANT ALL PRIVILEGES ON DATABASE intellidesk TO intellidesk;
\q
```

**Option B: SQLite (Quick Test)**

```powershell
# Edit backend/.env
DATABASE_URL=sqlite:///./intellidesk.db
```

### 4. Initialize Database

```powershell
cd backend
python -c "from database import init_db; init_db()"
```

### 5. Start Backend

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 6. Setup Frontend

Open a new terminal:

```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Testing the System

### Test Email Processing

1. Go to http://localhost:8000/docs
2. Find `/api/emails/process` endpoint
3. Click "Try it out"
4. Use this sample JSON:

```json
{
  "subject": "URGENT: App crashes when uploading files",
  "body": "Hi Support,\n\nOur production app crashes whenever users try to upload PDF files. This is affecting all users!\n\nError: 500 Internal Server Error\n\nPlease help ASAP!\n\nBest,\nJohn Smith\nIT Manager\njohn@techcorp.com",
  "sender": "john.smith@techcorp.com",
  "headers": {}
}
```

5. Click "Execute"
6. Check the response - you'll see:
   - Email classified (category + confidence)
   - Urgency detected (P1-P4)
   - AI-generated response
   - Ticket created

7. Go to http://localhost:3000 to see the ticket in the dashboard!

## Project Structure

```
IntelliDesk/
├── ai/                      # AI & NLP Module
│   ├── classifier.py        # Email classification
│   ├── urgency.py           # Urgency detection
│   ├── embeddings.py        # Vector embeddings
│   ├── deduplication.py     # Thread detection
│   ├── auto_reply.py        # Auto-response generation
│   └── config.py            # AI configuration
│
├── backend/                 # FastAPI Backend
│   ├── main.py              # Main application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database setup
│   ├── config.py            # Backend config
│   ├── routers/             # API endpoints
│   │   ├── emails.py
│   │   ├── tickets.py
│   │   └── analytics.py
│   └── services/            # Business logic
│       └── email_processor.py
│
└── frontend/                # React Frontend
    ├── src/
    │   ├── pages/
    │   │   ├── Dashboard.jsx
    │   │   └── TicketDetail.jsx
    │   ├── components/
    │   │   ├── TicketCard.jsx
    │   │   ├── UrgencyBadge.jsx
    │   │   └── ResponsePreview.jsx
    │   ├── services/
    │   │   └── api.js
    │   └── App.jsx
    └── package.json
```

## Environment Variables

### Backend (.env)

```env
# REQUIRED
GEMINI_API_KEY=your_gemini_api_key_here

# Database (choose one)
DATABASE_URL=postgresql://intellidesk:intellidesk123@localhost:5432/intellidesk
# OR for SQLite testing:
# DATABASE_URL=sqlite:///./intellidesk.db

# Redis (optional - for caching)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=change-this-to-a-random-secret-key

# Email SMTP (for sending responses)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=support@intellidesk.ai
```

## API Endpoints

### Email Processing

**POST /api/emails/process**
Process a single email

```json
{
  "subject": "string",
  "body": "string",
  "sender": "email@example.com",
  "headers": {}
}
```

**POST /api/emails/batch-process**
Process multiple emails

### Tickets

**GET /api/tickets/**
List all tickets (with pagination & filters)

**GET /api/tickets/{ticket_id}**
Get ticket details

**PATCH /api/tickets/{ticket_id}/status**
Update ticket status

**POST /api/tickets/{ticket_id}/notes**
Add internal note

### Analytics

**GET /api/analytics/dashboard**
Get dashboard statistics

**GET /api/analytics/trends**
Get ticket trends

**GET /api/analytics/performance**
Get AI performance metrics

## Docker Setup (Alternative)

```powershell
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Troubleshooting

### "Module not found" error

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### "Database connection failed"

```powershell
# Check PostgreSQL is running
# OR switch to SQLite in .env:
DATABASE_URL=sqlite:///./intellidesk.db
```

### "Gemini API error"

```powershell
# Verify API key in backend/.env
# Check key is valid at https://makersuite.google.com/app/apikey
```

### Frontend won't start

```powershell
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Team Workflow

### Member 1: AI Module

```powershell
git checkout -b ai-module
# Work on ai/ folder
git add ai/
git commit -m "Add urgency detection"
git push origin ai-module
```

### Member 2: Backend

```powershell
git checkout -b backend-module
# Work on backend/ folder
git add backend/
git commit -m "Add ticket API endpoints"
git push origin backend-module
```

### Member 3: Frontend

```powershell
git checkout -b frontend-module
# Work on frontend/ folder
git add frontend/
git commit -m "Add dashboard UI"
git push origin frontend-module
```

### Merging

```powershell
git checkout main
git pull origin main
git merge ai-module
git merge backend-module
git merge frontend-module
git push origin main
```

## Next Steps

1. Add email integration (Gmail API / IMAP)
2. Implement real email sending (SMTP)
3. Add user authentication
4. Deploy to cloud (AWS/GCP/Azure)
5. Add more FAQ entries
6. Implement ticket assignment
7. Add real-time notifications

## Support

For issues, check:

- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser console (F12)
- Database: Check data in PostgreSQL
- API: Test endpoints at http://localhost:8000/docs

---

**Made with ❤️ using Gemini AI**
