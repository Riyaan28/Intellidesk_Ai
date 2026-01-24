# 🚨 Urgency Classification - Quick Reference Card

## Signal Detection Cheat Sheet

### 🗣️ TONE DETECTION

| Signal                         | Trigger                 | Example                |
| ------------------------------ | ----------------------- | ---------------------- |
| ANGRY_TONE_HIGH_CAPS           | >50% caps               | "URGENT FIX THIS NOW"  |
| ELEVATED_TONE_CAPS             | >30% caps               | "PLEASE Help ASAP"     |
| MULTIPLE_CAPS_WORDS            | 3+ caps words           | "THIS IS REALLY BAD"   |
| VERY_HIGH_URGENCY_EXCLAMATIONS | 5+ !!!                  | "Help!!!!! Now!!!!!"   |
| HIGH_URGENCY_EXCLAMATIONS      | 3+ !!!                  | "Fix this!!!"          |
| EMOTIONAL_LANGUAGE             | frustrated, angry, etc. | "This is unacceptable" |

### ⏰ TIME SENSITIVITY

| Level    | Keywords                                             | Signal                  |
| -------- | ---------------------------------------------------- | ----------------------- |
| Critical | immediately, right now, asap, urgent, emergency, now | TIME_SENSITIVE_CRITICAL |
| High     | today, this morning, within hours, very soon         | TIME_SENSITIVE_HIGH     |
| Medium   | soon, quickly, prompt, expedite                      | TIME_SENSITIVE_MEDIUM   |

### 💼 BUSINESS IMPACT

| Type       | Keywords                                              | Signal                     |
| ---------- | ----------------------------------------------------- | -------------------------- |
| Revenue    | losing money, revenue loss, costing us, sales down    | BUSINESS_IMPACT_REVENUE    |
| Customers  | customers waiting, all users, everyone affected       | BUSINESS_IMPACT_CUSTOMERS  |
| Production | production down, system down, outage, offline, broken | BUSINESS_IMPACT_PRODUCTION |

### 🚨 ESCALATION KEYWORDS

| Category     | Keywords                                 | Action             |
| ------------ | ---------------------------------------- | ------------------ |
| Legal        | lawyer, attorney, sue, lawsuit           | → P1 Auto-escalate |
| Cancellation | cancel, terminate, end contract, switch  | → P1 Auto-escalate |
| Financial    | refund, chargeback, money back           | → P1 Auto-escalate |
| Social       | social media, review, BBB, tell everyone | → P1 Auto-escalate |

### 🔔 FOLLOW-UP TRACKING

| Count | Action                  | Display                             |
| ----- | ----------------------- | ----------------------------------- |
| 0     | Normal processing       | -                                   |
| 1     | Show warning            | 🔔 Follow-up #1                     |
| 2     | Show warning            | 🔔 Follow-up #2 (next = escalation) |
| 3+    | **AUTO-ESCALATE to P1** | ⚠️ ESCALATED                        |

## Severity Matrix

| Severity        | SLA | Auto-Escalate When                                                                  | Visual    |
| --------------- | --- | ----------------------------------------------------------------------------------- | --------- |
| **P1 Critical** | 1h  | • 3rd follow-up<br>• Production down<br>• Legal/cancel threats<br>• Security breach | 🔴 Red    |
| **P2 High**     | 4h  | • Major feature broken<br>• Blocking work<br>• High urgency signals                 | 🟡 Yellow |
| **P3 Medium**   | 24h | • Minor issues<br>• Normal requests                                                 | 🔵 Blue   |
| **P4 Low**      | 72h | • Feature requests<br>• Suggestions                                                 | 🟢 Green  |

## Frontend Indicators

### Dashboard (TicketCard)

```
[P1] ⚠️ ESCALATED          ← Red, bold
[P2] 🔔 Follow-up #2       ← Yellow
[P3]                       ← Blue
[P4]                       ← Green
```

### Ticket Detail

```
┌─────────────────────────────────┐
│ 🚨 AUTO-ESCALATED              │  Red box
│ Auto-escalated: 3rd follow-up  │
│ Follow-up #3                   │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 🔔 Follow-up #2                │  Yellow box
│ Next follow-up will trigger    │
│ auto-escalation to P1          │
└─────────────────────────────────┘

Urgency Signals:
• ANGRY_TONE_HIGH_CAPS
• TIME_SENSITIVE_CRITICAL
• BUSINESS_IMPACT_REVENUE
```

## Code Examples

### Detecting Urgency

```python
from ai.urgency import urgency_detector

result = urgency_detector.detect_urgency(
    subject="URGENT!!! System down",
    body="Production is completely broken!",
    category="Technical Support",
    followup_count=2
)

# result = {
#   'severity': 'P1',
#   'sla_hours': 1,
#   'auto_escalate': True,
#   'signals': ['ANGRY_TONE_HIGH_CAPS', ...],
#   'reasoning': 'Auto-escalated: Critical severity'
# }
```

### Checking Ticket

```python
if ticket.is_escalated:
    print(f"⚠️ ESCALATED: {ticket.escalation_reason}")
    print(f"Follow-ups: {ticket.followup_count}")
```

### Frontend React

```jsx
{
  ticket.is_escalated && (
    <span className="badge bg-red-600 text-white">⚠️ ESCALATED</span>
  );
}

{
  ticket.followup_count > 0 && (
    <span className="badge bg-yellow-600 text-white">
      🔔 Follow-up #{ticket.followup_count}
    </span>
  );
}
```

## Configuration

Edit `ai/ai_config.py`:

```python
# Customize SLA hours
SEVERITY_LEVELS = {
    "P1": {"name": "Critical", "sla_hours": 1},
    "P2": {"name": "High", "sla_hours": 4},
    # ...
}

# Add custom escalation keywords
ESCALATION_KEYWORDS = [
    "lawyer", "cancel", "refund",
    "your_custom_keyword",
    # ...
]
```

## Testing Quick Commands

```bash
# Simple test (no dependencies)
python test_urgency_simple.py

# Full test (requires colorama)
python test_urgency_system.py

# Database migration
cd backend
python migrate_add_escalation_fields.py
```

## Common Scenarios

### Scenario 1: Angry Customer

```
Input: "THIS IS RIDICULOUS!!! FIX THIS NOW!!!"
→ Signals: ANGRY_TONE_HIGH_CAPS, EMOTIONAL_LANGUAGE,
           HIGH_URGENCY_EXCLAMATIONS, TIME_SENSITIVE_CRITICAL
→ Result: P1 or P2 (based on AI analysis)
```

### Scenario 2: Legal Threat

```
Input: "I'm calling my lawyer if not fixed"
→ Signals: ESCALATION_KEYWORD_LAWYER
→ Result: P1 (Auto-escalated)
```

### Scenario 3: 3rd Follow-up

```
(Customer's 3rd email about same issue)
→ followup_count: 3
→ Result: P1 (Auto-escalated: 3rd follow-up)
```

### Scenario 4: Production Down

```
Input: "Production system down, all users affected"
→ Signals: BUSINESS_IMPACT_PRODUCTION, BUSINESS_IMPACT_CUSTOMERS
→ Result: P1 (Critical keywords matched)
```

---

**Print this for your desk! 📋**
