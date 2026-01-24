# API Documentation - IntelliDesk AI

Base URL: `http://localhost:8000`

## Authentication

Currently no authentication required. Add JWT tokens in production.

## Email Processing

### Process Single Email

**Endpoint:** `POST /api/emails/process`

**Request Body:**

```json
{
  "subject": "string",
  "body": "string",
  "sender": "email@example.com",
  "headers": {
    "Message-ID": "optional",
    "In-Reply-To": "optional",
    "References": "optional"
  },
  "received_at": "2024-01-24T10:00:00Z" // optional
}
```

**Response:**

```json
{
  "success": true,
  "ticket_id": "TKT-000001",
  "classification": {
    "category": "Technical Support",
    "confidence": 0.94,
    "subcategory": "Error/Bug",
    "requires_review": false,
    "reasoning": "Error code detected in message"
  },
  "urgency": {
    "severity": "P1",
    "severity_name": "Critical",
    "sla_hours": 1,
    "sla_deadline": "2024-01-24T11:00:00Z",
    "auto_escalate": true,
    "signals": ["TIME_SENSITIVE", "BUSINESS_IMPACT"],
    "reasoning": "Production issue affecting all users"
  },
  "deduplication": {
    "is_duplicate": false,
    "master_ticket_id": null,
    "similarity_score": null
  },
  "auto_response": {
    "response_type": "perfect_match",
    "response_text": "Dear Customer,\n\nThank you for...",
    "confidence": 0.96,
    "auto_send": true,
    "references": ["Video Tutorial: https://..."]
  },
  "customer_info": {
    "customer_id": 1,
    "company_name": "TechCorp Inc.",
    "tier": "Gold",
    "is_trial": false
  },
  "processing_time_ms": 1234.5
}
```

### Batch Process Emails

**Endpoint:** `POST /api/emails/batch-process`

**Request Body:**

```json
[
  {
    "subject": "Issue 1",
    "body": "Description...",
    "sender": "user1@example.com"
  },
  {
    "subject": "Issue 2",
    "body": "Description...",
    "sender": "user2@example.com"
  }
]
```

**Response:**

```json
{
  "total": 2,
  "processed": 2,
  "results": [
    {
      /* EmailProcessResponse */
    },
    {
      /* EmailProcessResponse */
    }
  ]
}
```

## Tickets

### List Tickets

**Endpoint:** `GET /api/tickets/`

**Query Parameters:**

- `page` (int, default=1): Page number
- `page_size` (int, default=20): Items per page
- `status` (string): Filter by status (New, In Progress, Resolved, Closed)
- `severity` (string): Filter by severity (P1, P2, P3, P4)
- `category` (string): Filter by category
- `search` (string): Search in subject/body/ticket_id

**Response:**

```json
{
  "total": 100,
  "tickets": [
    {
      "id": 1,
      "ticket_id": "TKT-000001",
      "subject": "App crashes",
      "body": "Description...",
      "sender": "user@example.com",
      "category": "Technical Support",
      "severity": "P1",
      "status": "New",
      "sla_deadline": "2024-01-24T11:00:00Z",
      "created_at": "2024-01-24T10:00:00Z",
      "classification_confidence": 0.94,
      "ai_response_text": "Response..."
    }
  ],
  "page": 1,
  "page_size": 20
}
```

### Get Ticket Details

**Endpoint:** `GET /api/tickets/{ticket_id}`

**Response:**

```json
{
  // All fields from TicketResponse plus:
  "subcategory": "Error/Bug",
  "classification_reasoning": "Error detected",
  "urgency_signals": ["TIME_SENSITIVE"],
  "urgency_reasoning": "Critical issue",
  "customer_company": "TechCorp Inc.",
  "customer_tier": "Gold",
  "thread_count": 2,
  "similar_tickets": [
    {
      "ticket_id": "TKT-000045",
      "subject": "Similar issue",
      "similarity": 0.87,
      "resolution": "Solution was..."
    }
  ]
}
```

### Update Ticket Status

**Endpoint:** `PATCH /api/tickets/{ticket_id}/status`

**Request Body:**

```json
{
  "status": "Resolved",
  "resolution": "Fixed by updating configuration" // optional
}
```

**Response:**

```json
{
  "success": true,
  "ticket_id": "TKT-000001",
  "status": "Resolved"
}
```

### Add Internal Note

**Endpoint:** `POST /api/tickets/{ticket_id}/notes`

**Request Body:**

```json
{
  "note": "Customer called for follow-up. Confirmed issue resolved."
}
```

**Response:**

```json
{
  "success": true,
  "ticket_id": "TKT-000001"
}
```

### Get Ticket Thread

**Endpoint:** `GET /api/tickets/{ticket_id}/thread`

**Response:**

```json
{
  "ticket_id": "TKT-000001",
  "thread_count": 3,
  "emails": [
    {
      "ticket_id": "TKT-000001",
      "subject": "Original issue",
      "body": "...",
      "sender": "user@example.com",
      "created_at": "2024-01-24T10:00:00Z"
    },
    {
      "ticket_id": "TKT-000023",
      "subject": "Re: Original issue",
      "body": "Follow-up...",
      "sender": "user@example.com",
      "created_at": "2024-01-24T12:00:00Z"
    }
  ]
}
```

## Analytics

### Dashboard Statistics

**Endpoint:** `GET /api/analytics/dashboard`

**Response:**

```json
{
  "total_tickets_today": 45,
  "total_tickets_week": 312,
  "avg_response_time": 27.5,
  "sla_compliance_rate": 92.3,
  "auto_response_rate": 67.8,
  "top_categories": [
    {
      "category": "Technical Support",
      "count": 156
    },
    {
      "category": "Billing/Invoice",
      "count": 89
    }
  ],
  "severity_distribution": {
    "P1": 5,
    "P2": 12,
    "P3": 23,
    "P4": 5
  },
  "recent_tickets": [
    /* Array of TicketResponse */
  ]
}
```

### Ticket Trends

**Endpoint:** `GET /api/analytics/trends`

**Query Parameters:**

- `days` (int, default=30): Number of days to analyze

**Response:**

```json
{
  "daily_counts": [
    {
      "date": "2024-01-24",
      "count": 45
    },
    {
      "date": "2024-01-23",
      "count": 38
    }
  ],
  "category_trends": [
    {
      "date": "2024-01-24",
      "category": "Technical Support",
      "count": 23
    }
  ]
}
```

### Performance Metrics

**Endpoint:** `GET /api/analytics/performance`

**Response:**

```json
{
  "total_tickets": 1234,
  "avg_classification_confidence": 0.87,
  "manual_review_rate": 12.5,
  "auto_response_rate": 67.8,
  "threads_detected": 234,
  "response_type_distribution": {
    "perfect_match": 456,
    "partial_match": 234,
    "resolution_based": 123,
    "acknowledgment": 421
  }
}
```

## System

### Health Check

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "database": "healthy",
  "ai_service": "healthy",
  "vector_db": "healthy (123 tickets indexed)",
  "timestamp": "2024-01-24T10:00:00Z"
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

No rate limiting currently. Add in production.

## WebSocket Support

Not implemented. Add for real-time updates.

## Examples

### cURL Examples

```bash
# Process email
curl -X POST http://localhost:8000/api/emails/process \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "App crashes",
    "body": "Help! App crashes when uploading files",
    "sender": "user@example.com"
  }'

# Get tickets
curl http://localhost:8000/api/tickets/?severity=P1

# Update status
curl -X PATCH http://localhost:8000/api/tickets/TKT-000001/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Resolved"}'
```

### Python Examples

```python
import requests

# Process email
response = requests.post(
    "http://localhost:8000/api/emails/process",
    json={
        "subject": "App crashes",
        "body": "Help! App crashes when uploading files",
        "sender": "user@example.com"
    }
)
result = response.json()
print(f"Ticket created: {result['ticket_id']}")
print(f"Category: {result['classification']['category']}")
print(f"Severity: {result['urgency']['severity']}")

# Get dashboard stats
stats = requests.get("http://localhost:8000/api/analytics/dashboard").json()
print(f"Today's tickets: {stats['total_tickets_today']}")
```

### JavaScript Examples

```javascript
// Process email
const response = await fetch("http://localhost:8000/api/emails/process", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    subject: "App crashes",
    body: "Help! App crashes when uploading files",
    sender: "user@example.com",
  }),
});

const result = await response.json();
console.log(`Ticket: ${result.ticket_id}`);
console.log(`Category: ${result.classification.category}`);
```
