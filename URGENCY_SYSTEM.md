# Urgency & Severity Classification System

## Overview

The IntelliDesk urgency detection system automatically classifies support tickets into 4 severity levels (P1-P4) based on comprehensive signal detection and dynamic analysis.

## Severity Levels & SLA

| Severity          | Description                         | SLA      | Examples                                          |
| ----------------- | ----------------------------------- | -------- | ------------------------------------------------- |
| **P1 (Critical)** | Production down, all users affected | 1 Hour   | System outage, data breach, revenue loss          |
| **P2 (High)**     | Major feature broken, blocking work | 4 Hours  | Important feature broken, multiple users affected |
| **P3 (Medium)**   | Minor issue, workaround available   | 24 Hours | Non-critical bugs, minor issues                   |
| **P4 (Low)**      | Feature request, nice-to-have       | 72 Hours | Suggestions, enhancements                         |

## Dynamic Signal Detection

### 1. **Tone Detection** 🗣️

Analyzes emotional tone and urgency indicators in the email:

- **ALL CAPS Detection**: High caps ratio indicates anger/urgency
  - `>50% caps`: ANGRY_TONE_HIGH_CAPS
  - `>30% caps`: ELEVATED_TONE_CAPS
  - Multiple caps words (3+): MULTIPLE_CAPS_WORDS

- **Exclamation Marks**: Shows urgency/frustration
  - `5+`: VERY_HIGH_URGENCY_EXCLAMATIONS
  - `3+`: HIGH_URGENCY_EXCLAMATIONS

- **Emotional Language**: Detects frustrated/angry words
  - Keywords: frustrated, unacceptable, disappointed, angry, furious, ridiculous, terrible, horrible, worst
  - Signal: EMOTIONAL_LANGUAGE

**Examples:**

```
"URGENT!!! SYSTEM IS DOWN!!!" → High urgency, angry tone
"This is COMPLETELY UNACCEPTABLE!!!" → Elevated tone, emotional language
```

### 2. **Time Sensitivity** ⏰

Identifies urgency based on time-related keywords:

- **Critical**: immediately, right now, asap, urgent, emergency, now
- **High**: today, this morning, this afternoon, within hours, very soon
- **Medium**: soon, quickly, prompt, expedite

**Examples:**

```
"Need fix IMMEDIATELY" → TIME_SENSITIVE_CRITICAL
"Please resolve today" → TIME_SENSITIVE_HIGH
"Fix this soon" → TIME_SENSITIVE_MEDIUM
```

### 3. **Business Impact** 💼

Detects impact on revenue, customers, or production:

- **Revenue**: losing money, revenue loss, financial impact, costing us, sales down
- **Customers**: customers waiting, customer complaints, all users, everyone affected
- **Production**: production down, system down, outage, offline, not working, broken

**Examples:**

```
"We're losing money every hour!" → BUSINESS_IMPACT_REVENUE
"All users are affected" → BUSINESS_IMPACT_CUSTOMERS
"Production system is down" → BUSINESS_IMPACT_PRODUCTION
```

### 4. **Escalation Keywords** 🚨

Triggers auto-escalation on serious threats:

- **Legal**: lawyer, attorney, legal action, sue, lawsuit
- **Cancellation**: cancel, terminate, end contract, switch
- **Financial**: refund, chargeback, money back, compensation
- **Emotional**: unacceptable, frustrated, angry, furious, outraged
- **Escalation Actions**: complaint, escalate, manager, supervisor, CEO
- **Public Threats**: social media, review, BBB, tell everyone

**Examples:**

```
"I'm contacting my lawyer" → ESCALATION_KEYWORD_LAWYER → Auto-escalate to P1
"Cancel my account and refund" → ESCALATION_KEYWORD_CANCEL, ESCALATION_KEYWORD_REFUND
"Posting this on social media" → ESCALATION_KEYWORD_SOCIAL_MEDIA
```

### 5. **Follow-up Tracking** 🔔

Automatically tracks and escalates repeated follow-ups:

- Counts non-resolved tickets from same sender in last 7 days
- **3rd follow-up**: Auto-escalates to P1 (Critical)
- Displays follow-up count on dashboard and ticket detail

**Example:**

```
1st email: Classified normally
2nd email: Shows "Follow-up #1" badge
3rd email: AUTO-ESCALATED to P1 → "Auto-escalated: 3rd follow-up"
```

## Auto-Escalation Rules

The system automatically escalates tickets to P1 (Critical) in these scenarios:

1. **3rd Follow-up**: Customer has sent 3+ emails about open tickets
2. **Critical Keywords**: Production down, all users affected, emergency
3. **Legal/Cancellation Threats**: Lawyer, cancel, refund keywords
4. **Business Impact**: Losing money, revenue loss, system down

When escalated, the ticket is marked with:

- `is_escalated`: true
- `escalation_reason`: Why it was escalated
- `escalation_time`: When escalation occurred

## Usage

### Backend (Python)

```python
from ai.urgency import urgency_detector

# Detect urgency
result = urgency_detector.detect_urgency(
    subject="URGENT! System down!!!",
    body="Production system is completely down. All users affected!",
    category="Technical Support",
    followup_count=2  # 2nd follow-up
)

print(result)
# {
#     'severity': 'P1',
#     'severity_name': 'Critical',
#     'sla_hours': 1,
#     'sla_deadline': datetime,
#     'auto_escalate': True,
#     'signals': ['ANGRY_TONE_HIGH_CAPS', 'BUSINESS_IMPACT_PRODUCTION', ...],
#     'reasoning': 'Auto-escalated: 2nd follow-up'
# }
```

### Frontend (React)

The TicketCard and TicketDetail components automatically display:

**Dashboard (TicketCard):**

- Severity badge (P1-P4)
- Escalation alert: ⚠️ ESCALATED
- Follow-up indicator: 🔔 Follow-up #2

**Ticket Detail:**

- Full signal list
- Escalation reason
- Follow-up count with warning
- SLA countdown

## Database Schema

New fields added to `tickets` table:

```sql
followup_count INTEGER DEFAULT 0
is_escalated BOOLEAN DEFAULT FALSE
escalation_reason VARCHAR(255)
escalation_time TIMESTAMP WITH TIME ZONE
```

## Testing

Run the comprehensive test suite:

```bash
python test_urgency_system.py
```

This tests:

- ✅ ALL CAPS detection
- ✅ Business impact (revenue, customers, production)
- ✅ Escalation keywords (lawyer, refund, cancel)
- ✅ 3rd follow-up auto-escalation
- ✅ Time sensitivity
- ✅ Emotional language
- ✅ Multiple exclamations
- ✅ P3/P4 classification

## Configuration

Customize in `ai/ai_config.py`:

```python
# Severity Levels
SEVERITY_LEVELS = {
    "P1": {"name": "Critical", "sla_hours": 1},
    "P2": {"name": "High", "sla_hours": 4},
    "P3": {"name": "Medium", "sla_hours": 24},
    "P4": {"name": "Low", "sla_hours": 72}
}

# Escalation Keywords (customize as needed)
ESCALATION_KEYWORDS = [
    "lawyer", "cancel", "refund", "sue", ...
]
```

## Migration

Run this to add new columns to existing database:

```bash
cd backend
python migrate_add_escalation_fields.py
```

## Examples

### Example 1: Critical Emergency

```
Subject: URGENT!!! PRODUCTION DOWN!!!
Body: THE ENTIRE SYSTEM IS DOWN! ALL USERS CANNOT ACCESS ANYTHING!

→ P1 (Critical)
→ Signals: ANGRY_TONE_HIGH_CAPS, BUSINESS_IMPACT_PRODUCTION
→ SLA: 1 hour
→ Auto-escalate: YES
```

### Example 2: Legal Threat

```
Subject: Final Warning
Body: This is unacceptable. I've contacted my lawyer and need immediate refund.

→ P1 (Critical)
→ Signals: ESCALATION_KEYWORD_LAWYER, ESCALATION_KEYWORD_REFUND
→ SLA: 1 hour
→ Auto-escalate: YES
```

### Example 3: 3rd Follow-up

```
Subject: Re: Re: Re: Still broken
Body: This is the third time I'm reaching out. Nothing is being done.

→ P1 (Critical)
→ Signals: 3rd follow-up - auto escalation
→ SLA: 1 hour
→ Auto-escalate: YES
→ Reason: "Auto-escalated: 3rd follow-up"
```

### Example 4: Feature Request

```
Subject: Suggestion
Body: Would be nice to have a dark mode option. Not urgent.

→ P4 (Low)
→ Signals: []
→ SLA: 72 hours
→ Auto-escalate: NO
```

## Benefits

1. **Automated Triage**: No manual severity assignment needed
2. **Dynamic Detection**: Goes beyond simple keywords to understand context
3. **Escalation Protection**: Prevents frustrated customers from churning
4. **SLA Management**: Clear deadlines for each severity level
5. **Visibility**: Dashboard shows escalations and follow-ups at a glance
6. **Customer Experience**: Ensures critical issues get immediate attention

## Future Enhancements

- [ ] Machine learning model for tone detection
- [ ] Sentiment analysis integration
- [ ] Customer tier-based priority adjustment
- [ ] Historical pattern recognition
- [ ] Multi-language support
