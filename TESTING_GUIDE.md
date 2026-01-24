# 🧪 IntelliDesk AI - Testing Guide

## Quick Test Commands

### 1. Health Check

```powershell
curl http://localhost:8000/health -UseBasicParsing
```

### 2. Process Test Emails

**Urgent Technical Issue:**

```powershell
$body = @{
    subject = "URGENT: Production server down!"
    body = "Our main production server crashed. All services are offline. Need immediate assistance!"
    sender = "admin@company.com"
} | ConvertTo-Json

curl -Method POST -Uri "http://localhost:8000/api/emails/process" `
     -Body $body -ContentType "application/json" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Billing Question:**

```powershell
$body = @{
    subject = "Question about my invoice"
    body = "I received an invoice for $500 but I thought my plan was $300/month. Can you clarify?"
    sender = "finance@startup.io"
} | ConvertTo-Json

curl -Method POST -Uri "http://localhost:8000/api/emails/process" `
     -Body $body -ContentType "application/json" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Feature Request:**

```powershell
$body = @{
    subject = "Feature request: Dark mode"
    body = "Would love to see a dark mode option in the dashboard. Many users work at night."
    sender = "user@example.com"
} | ConvertTo-Json

curl -Method POST -Uri "http://localhost:8000/api/emails/process" `
     -Body $body -ContentType "application/json" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Bug Report:**

```powershell
$body = @{
    subject = "App crashes when uploading large files"
    body = "Whenever I try to upload files larger than 50MB, the app freezes and crashes. Error code: ERR_UPLOAD_FAILED"
    sender = "developer@techcorp.com"
} | ConvertTo-Json

curl -Method POST -Uri "http://localhost:8000/api/emails/process" `
     -Body $body -ContentType "application/json" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 3. Get All Tickets

```powershell
curl -Uri "http://localhost:8000/api/tickets/" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### 4. Get Dashboard Stats

```powershell
curl -Uri "http://localhost:8000/api/analytics/dashboard" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 5. Get Specific Ticket Details

```powershell
# Replace 1 with actual ticket ID
curl -Uri "http://localhost:8000/api/tickets/1" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 6. Update Ticket Status

```powershell
$update = @{
    status = "In Progress"
    assigned_to = "support-agent-1"
} | ConvertTo-Json

curl -Method PATCH -Uri "http://localhost:8000/api/tickets/1/status" `
     -Body $update -ContentType "application/json" -UseBasicParsing
```

### 7. Test Batch Processing

```powershell
$batch = @{
    emails = @(
        @{
            subject = "Can't login"
            body = "Forgot my password"
            sender = "user1@test.com"
        },
        @{
            subject = "Pricing question"
            body = "How much is the enterprise plan?"
            sender = "sales@corp.com"
        },
        @{
            subject = "Feature suggestion"
            body = "Please add export to PDF"
            sender = "user2@test.com"
        }
    )
} | ConvertTo-Json -Depth 10

curl -Method POST -Uri "http://localhost:8000/api/emails/batch-process" `
     -Body $batch -ContentType "application/json" -UseBasicParsing |
     Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## What to Expect

### ✅ Successful Email Processing Response:

```json
{
  "success": true,
  "ticket_id": "TKT-000001",
  "classification": {
    "category": "Technical Support",
    "confidence": 0.95,
    "subcategory": "Error/Bug",
    "requires_review": false,
    "reasoning": "AI classified as technical issue"
  },
  "urgency": {
    "severity": "P1",
    "severity_name": "Critical",
    "sla_hours": 1,
    "auto_escalate": true
  },
  "deduplication": {
    "is_duplicate": false
  },
  "auto_response": {
    "response_type": "faq_match",
    "auto_send": true,
    "confidence": 0.92
  },
  "customer_info": {
    "company_name": "Company",
    "tier": "Gold"
  }
}
```

## Testing Categories

### 📧 Email Categories to Test:

1. **Technical Support** - bugs, errors, crashes
2. **Billing/Invoice** - payment, invoice, refund
3. **Feature Request** - new features, enhancements
4. **How-To/Documentation** - questions, guides
5. **Access Request** - permissions, login issues
6. **General Inquiry** - general questions
7. **Feedback** - suggestions, reviews
8. **Sales** - pricing, demos
9. **Account Management** - settings, profile

### 🚨 Urgency Levels to Test:

- **P1 (Critical)**: Use words like "URGENT", "DOWN", "PRODUCTION", "CRITICAL"
- **P2 (High)**: Business impact, blocking work
- **P3 (Medium)**: Important but not blocking
- **P4 (Low)**: General questions, feature requests

## Frontend Testing

### Dashboard Features:

1. **View all tickets** - http://localhost:3000
2. **Filter by severity** - Use P1/P2/P3/P4 filters
3. **Search tickets** - Search bar functionality
4. **View ticket details** - Click on any ticket
5. **See AI reasoning** - View classification confidence
6. **Check auto-responses** - See generated responses

## API Documentation

Interactive API docs available at: http://localhost:8000/docs

Try each endpoint:

- ✅ `/health` - Health check
- ✅ `/api/test-email` - Quick test endpoint
- ✅ `/api/emails/process` - Process single email
- ✅ `/api/emails/batch-process` - Process multiple emails
- ✅ `/api/tickets/` - Get all tickets
- ✅ `/api/tickets/{id}` - Get ticket details
- ✅ `/api/analytics/dashboard` - Dashboard stats

## Database Location

SQLite database stored at: `backend/intellidesk.db`

View with SQLite browser or command:

```powershell
sqlite3 backend\intellidesk.db "SELECT * FROM tickets;"
```

## Troubleshooting

### Backend not responding?

```powershell
# Check if running
Get-Process python* | Where-Object {$_.Path -like "*Intellidesk*"}

# Restart backend
& backend\venv\Scripts\python.exe run_backend.py
```

### Frontend not loading?

```powershell
# Check if running
Get-Process node* | Where-Object {$_.Path -like "*Intellidesk*"}

# Restart frontend
cd frontend
npm run dev
```

### API Key issues?

Check `backend\.env` has valid GEMINI_API_KEY

## Performance Testing

Process multiple emails to test performance:

```powershell
1..10 | ForEach-Object {
    $body = @{
        subject = "Test email $_"
        body = "This is test email number $_"
        sender = "test$_@example.com"
    } | ConvertTo-Json

    curl -Method POST -Uri "http://localhost:8000/api/emails/process" `
         -Body $body -ContentType "application/json" -UseBasicParsing
}
```

## Success Metrics

After testing, you should see:

- ✅ Emails classified with 80%+ confidence
- ✅ Correct urgency levels assigned
- ✅ Auto-responses generated
- ✅ No duplicate tickets created
- ✅ Customer information auto-populated
- ✅ SLA deadlines calculated
- ✅ Dashboard shows real-time stats

---

**Happy Testing! 🚀**
