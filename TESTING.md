# IntelliDesk AI - Testing Guide

## Test Email Samples

Use these sample emails to test all features:

### 1. Critical Technical Issue (P1)

```json
{
  "subject": "URGENT: Production server down - all users affected",
  "body": "EMERGENCY!!!\n\nOur production server is completely down. ALL USERS are unable to access the application.\n\nError: Connection timeout\nAffected users: 500+\nTime down: 30 minutes\n\nThis is causing MAJOR revenue loss. Need immediate help!!!\n\nJohn Smith\nCTO\nTechCorp Inc.\njohn.smith@techcorp.com\n+1-555-0123",
  "sender": "john.smith@techcorp.com"
}
```

**Expected Result:**

- Category: Hardware/Infrastructure or Technical Support
- Severity: P1 (Critical)
- SLA: 1 hour
- Urgency Signals: ALL_CAPS, BUSINESS_IMPACT, TIME_SENSITIVE
- Auto-escalate: Yes

### 2. Billing Query (P3)

```json
{
  "subject": "Request for invoice - January 2024",
  "body": "Hi Support Team,\n\nCould you please send me the invoice for January 2024?\n\nCompany: Acme Corp\nBilling email: billing@acmecorp.com\n\nThank you!\n\nBest regards,\nSarah Johnson\nFinance Manager\nAcme Corporation\nsarah.johnson@acmecorp.com",
  "sender": "sarah.johnson@acmecorp.com"
}
```

**Expected Result:**

- Category: Billing/Invoice
- Severity: P3 (Medium)
- SLA: 24 hours
- Auto-response: Yes (high confidence)

### 3. How-To Question (P4)

```json
{
  "subject": "How do I export data to Excel?",
  "body": "Hello,\n\nI'm trying to export our monthly reports to Excel format but can't find the option.\n\nCould you please guide me on how to do this?\n\nThanks,\nMike Chen\nmike.chen@innovate.io",
  "sender": "mike.chen@innovate.io"
}
```

**Expected Result:**

- Category: How-To/Documentation
- Severity: P4 (Low)
- SLA: 72 hours
- Auto-response: Perfect match from FAQ
- Auto-send: Yes (confidence >95%, severity P4)

### 4. Password Reset (P3)

```json
{
  "subject": "Need to reset my password",
  "body": "Hi,\n\nI forgot my password and need to reset it. Can you help?\n\nEmail: alex.wong@datatech.com\n\nThanks,\nAlex Wong",
  "sender": "alex.wong@datatech.com"
}
```

**Expected Result:**

- Category: Access Request
- Severity: P3 (Medium)
- Auto-response: Perfect match from FAQ
- Auto-send: Yes

### 5. Complaint/Escalation (P2)

```json
{
  "subject": "Very disappointed with service - 3rd follow-up",
  "body": "This is my THIRD email about this issue and I still haven't received a response!\n\nI'm extremely frustrated and disappointed. If this isn't resolved soon, I'll have to consider canceling our subscription.\n\nOriginal issue: Data export feature not working for 2 weeks.\n\nThis is unacceptable for a paid service.\n\nDr. Emily Roberts\nResearch Director\nemily.roberts@research.edu",
  "sender": "emily.roberts@research.edu"
}
```

**Expected Result:**

- Category: Complaint/Escalation
- Severity: P2 (High)
- Auto-escalate: Yes (escalation keywords + 3rd follow-up)
- Urgency Signals: ESCALATION_LANGUAGE, MULTIPLE_EXCLAMATIONS

### 6. Thread Detection Test

First email:

```json
{
  "subject": "App crashes when uploading large PDFs",
  "body": "Hi Support,\n\nThe application crashes whenever I try to upload PDF files larger than 10MB.\n\nBrowser: Chrome\nVersion: 1.2.3\n\nPlease help!\n\nTom Anderson\ntom@enterprise.com",
  "sender": "tom@enterprise.com"
}
```

Follow-up (should be detected as duplicate):

```json
{
  "subject": "Re: App crashes when uploading large PDFs",
  "body": "Hi,\n\nJust following up on my previous email about PDF upload crashes.\n\nAny update?\n\nTom",
  "sender": "tom@enterprise.com",
  "headers": {
    "In-Reply-To": "<previous-message-id@mail.com>",
    "References": "<previous-message-id@mail.com>"
  }
}
```

**Expected Result:**

- Second email detected as duplicate
- Merged into existing ticket
- Thread count: 1

### 7. Spam Detection Test

```json
{
  "subject": "Congratulations! You've won $1,000,000!!!",
  "body": "Click here to claim your prize now! Limited time offer!\n\nUnsubscribe here: spam.com",
  "sender": "noreply@spam-domain.com"
}
```

**Expected Result:**

- Detected as spam
- No ticket created
- Success: false

## Testing Workflow

### 1. Single Email Test

1. Start backend: `uvicorn main:app --reload`
2. Go to http://localhost:8000/docs
3. Test `/api/emails/process` endpoint
4. Use samples above
5. Verify response

### 2. Batch Processing Test

```json
POST /api/emails/batch-process

[
  { /* Email 1 */ },
  { /* Email 2 */ },
  { /* Email 3 */ }
]
```

### 3. Frontend Integration Test

1. Start frontend: `npm run dev`
2. Go to http://localhost:3000
3. Process test emails via API
4. Verify tickets appear in dashboard
5. Click on ticket for details
6. Check AI reasoning overlay
7. Verify response preview
8. Test status updates

### 4. Deduplication Test

Process emails in this order:

1. Original email
2. Reply with same subject
3. Another email from same sender with similar content
4. Email with ticket reference #TKT-000001

Verify:

- Original creates new ticket
- Reply merges into original
- Similar email merges (if within 72h)
- Ticket reference email merges

### 5. Performance Test

Test with 50 emails:

```python
import requests
import time

emails = []
for i in range(50):
    emails.append({
        "subject": f"Test issue #{i}",
        "body": f"This is test email number {i} for performance testing.",
        "sender": f"user{i}@test.com"
    })

start = time.time()
response = requests.post(
    "http://localhost:8000/api/emails/batch-process",
    json=emails
)
end = time.time()

result = response.json()
print(f"Processed {result['processed']} emails in {end-start:.2f} seconds")
print(f"Average time per email: {(end-start)/50:.2f}s")
```

**Success Criteria:**

- All 50 emails processed successfully
- No errors
- Average processing time < 2 seconds per email

## Verification Checklist

### Email Classification ✓

- [ ] Technical issues classified correctly
- [ ] Billing queries recognized
- [ ] Access requests identified
- [ ] How-to questions detected
- [ ] Spam filtered out
- [ ] Confidence scores > 80% for clear cases
- [ ] Confidence < 80% triggers manual review

### Urgency Detection ✓

- [ ] P1 assigned to critical issues
- [ ] P2 for high priority
- [ ] P3 for medium priority
- [ ] P4 for low priority
- [ ] ALL CAPS detected
- [ ] Exclamation marks counted
- [ ] Business impact keywords recognized
- [ ] Escalation keywords flagged

### Deduplication ✓

- [ ] Same subject detected
- [ ] Email headers parsed
- [ ] Ticket references found
- [ ] Same sender within 48h grouped
- [ ] Semantic similarity > 85% merged
- [ ] Thread count incremented

### Auto-Response ✓

- [ ] FAQ matches found
- [ ] Perfect matches (>90%) get full solution
- [ ] Partial matches (60-90%) get suggestions
- [ ] No matches get acknowledgment
- [ ] Confidence >95% + P3/P4 auto-sent
- [ ] References included
- [ ] Personalization working

### Customer Identification ✓

- [ ] Domain extracted
- [ ] Company name detected
- [ ] User info parsed from signature
- [ ] New customers flagged as leads
- [ ] Tier assigned

### UI/UX ✓

- [ ] Dashboard loads
- [ ] Tickets displayed correctly
- [ ] Urgency badges colored correctly
- [ ] SLA countdown working
- [ ] Confidence scores shown
- [ ] Response preview visible
- [ ] Similar tickets listed
- [ ] Status updates work

## Error Scenarios

Test these error cases:

### 1. Invalid Email

```json
{
  "subject": "",
  "body": "",
  "sender": "not-an-email"
}
```

### 2. Missing Required Fields

```json
{
  "subject": "Test"
}
```

### 3. Very Long Email

```json
{
  "subject": "Test",
  "body": "A".repeat(50000),
  "sender": "test@test.com"
}
```

### 4. Special Characters

```json
{
  "subject": "Test 中文 🚀 <script>alert('xss')</script>",
  "body": "Special chars: àéîöü",
  "sender": "test@test.com"
}
```

## Integration Tests

### Email API Integration

Test Gmail API integration (if implemented):

```python
from googleapiclient.discovery import build

# Fetch emails
service = build('gmail', 'v1', credentials=creds)
results = service.users().messages().list(userId='me').execute()

# Process each email
for msg in results['messages']:
    email_data = get_email_data(msg['id'])
    process_email(email_data)
```

### Database Tests

```python
from backend.database import SessionLocal
from backend.models import Ticket

db = SessionLocal()

# Test ticket creation
tickets = db.query(Ticket).all()
assert len(tickets) > 0

# Test filtering
p1_tickets = db.query(Ticket).filter(Ticket.severity == 'P1').all()
assert all(t.severity == 'P1' for t in p1_tickets)

# Test relationships
ticket = db.query(Ticket).first()
assert ticket.customer is not None
assert ticket.user is not None
```

## Load Testing

Use locust or k6 for load testing:

```python
from locust import HttpUser, task, between

class EmailUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def process_email(self):
        self.client.post("/api/emails/process", json={
            "subject": "Test",
            "body": "Test email",
            "sender": "test@test.com"
        })

    @task
    def get_dashboard(self):
        self.client.get("/api/analytics/dashboard")
```

Run: `locust -f load_test.py --host=http://localhost:8000`

## Success Metrics

After testing, verify:

- ✅ 100% email processing success rate
- ✅ Classification accuracy > 85%
- ✅ Urgency detection accuracy > 85%
- ✅ Zero duplicate tickets
- ✅ Auto-response rate > 60%
- ✅ Processing time < 30 seconds per email
- ✅ SLA compliance tracking working
- ✅ UI responsive and error-free
