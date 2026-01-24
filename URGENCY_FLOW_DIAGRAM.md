# Urgency Classification System - Flow Diagram

## Email Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCOMING EMAIL                                │
│  Subject: "URGENT!!! System down!!!"                            │
│  Body: "Production is completely down! All users affected!"     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: FOLLOW-UP DETECTION                        │
│  • Count recent non-resolved tickets from sender               │
│  • Result: followup_count = 2                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: SIGNAL DETECTION                           │
│                                                                  │
│  🗣️  TONE ANALYSIS                                              │
│      ✓ ANGRY_TONE_HIGH_CAPS (>50% caps)                        │
│      ✓ VERY_HIGH_URGENCY_EXCLAMATIONS (5+ !!!)                 │
│                                                                  │
│  ⏰ TIME SENSITIVITY                                            │
│      ✓ TIME_SENSITIVE_CRITICAL (keywords: urgent)              │
│                                                                  │
│  💼 BUSINESS IMPACT                                             │
│      ✓ BUSINESS_IMPACT_PRODUCTION (system down)                │
│      ✓ BUSINESS_IMPACT_CUSTOMERS (all users affected)          │
│                                                                  │
│  🚨 ESCALATION CHECK                                            │
│      ✗ No escalation keywords                                  │
│                                                                  │
│  🔔 FOLLOW-UP CHECK                                             │
│      ⚠️  2nd follow-up (next will trigger escalation)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 3: SEVERITY CLASSIFICATION                    │
│                                                                  │
│  IF: followup_count >= 3                                        │
│      → P1 + Auto-escalate ❌ (only 2 follow-ups)               │
│                                                                  │
│  IF: Critical keywords detected                                 │
│      → P1 + Auto-escalate ✅ (production down, all users)      │
│                                                                  │
│  RESULT: P1 (Critical)                                          │
│          SLA: 1 hour                                            │
│          Auto-escalate: YES                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: TICKET CREATION                            │
│                                                                  │
│  ticket_id: TKT-000123                                          │
│  severity: P1                                                   │
│  severity_name: "Critical"                                      │
│  sla_hours: 1                                                   │
│  sla_deadline: 2026-01-24 15:30                                │
│  followup_count: 2                                              │
│  is_escalated: TRUE                                             │
│  escalation_reason: "Auto-escalated: Critical severity"        │
│  urgency_signals: [ANGRY_TONE_HIGH_CAPS, ...]                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 5: FRONTEND DISPLAY                           │
│                                                                  │
│  Dashboard (TicketCard):                                        │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ TKT-000123  [P1]  ⚠️ ESCALATED  🔔 Follow-up #2      │   │
│  │ URGENT!!! System down!!!                               │   │
│  │ Production is completely down! All users affected!     │   │
│  │ 📧 user@company.com  ⏰ 0.5h remaining                │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Ticket Detail Page:                                            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Severity: P1 (Critical) | SLA: 1 hour | 0.5h remaining│   │
│  │                                                         │   │
│  │ 🚨 AUTO-ESCALATED                                      │   │
│  │ Auto-escalated: Critical severity                      │   │
│  │ Follow-up #2                                           │   │
│  │                                                         │   │
│  │ Urgency Signals:                                       │   │
│  │ • ANGRY_TONE_HIGH_CAPS                                 │   │
│  │ • VERY_HIGH_URGENCY_EXCLAMATIONS                       │   │
│  │ • TIME_SENSITIVE_CRITICAL                              │   │
│  │ • BUSINESS_IMPACT_PRODUCTION                           │   │
│  │ • BUSINESS_IMPACT_CUSTOMERS                            │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Escalation Scenarios

### Scenario A: 3rd Follow-up

```
Email 1 (Day 1): "My feature is broken"
  → P3, followup_count=0, is_escalated=FALSE

Email 2 (Day 2): "Still not fixed"
  → P3, followup_count=1, is_escalated=FALSE
  → Shows: 🔔 Follow-up #1

Email 3 (Day 3): "Third time asking!"
  → P1, followup_count=2, is_escalated=TRUE
  → Shows: ⚠️ ESCALATED
  → Reason: "Auto-escalated: 3rd follow-up"
```

### Scenario B: Legal Threat

```
Email: "Unacceptable! Calling my lawyer and demanding refund"
  → Detects: ESCALATION_KEYWORD_LAWYER, ESCALATION_KEYWORD_REFUND
  → P1, is_escalated=TRUE
  → Reason: "Auto-escalated: Escalation keywords detected"
```

### Scenario C: Business Impact

```
Email: "We're losing $10,000/hour with system down!"
  → Detects: BUSINESS_IMPACT_REVENUE, BUSINESS_IMPACT_PRODUCTION
  → P1, is_escalated=TRUE
  → Reason: "Auto-escalated: Critical severity"
```

## Signal Detection Matrix

| Signal Type             | Low   | Medium        | High           | Critical          |
| ----------------------- | ----- | ------------- | -------------- | ----------------- |
| **Caps Ratio**          | 0-30% | 30-50%        | 50%+           | -                 |
| **Exclamations**        | 0-2   | 3-4           | 5+             | -                 |
| **Time Keywords**       | -     | soon, quickly | today          | urgent, asap, now |
| **Business Impact**     | -     | minor issue   | feature broken | production down   |
| **Follow-ups**          | 0     | 1             | 2              | 3+ → P1           |
| **Escalation Keywords** | -     | -             | -              | lawyer, cancel    |

## Auto-Escalation Decision Tree

```
                    Incoming Email
                         │
                         ▼
              ┌──────────────────────┐
              │ followup_count >= 3? │
              └──────────────────────┘
                    │          │
                   YES        NO
                    │          │
                    ▼          ▼
                   P1    ┌─────────────────┐
                  Auto   │ Escalation      │
                         │ keywords?       │
                         └─────────────────┘
                              │        │
                             YES      NO
                              │        │
                              ▼        ▼
                             P1   ┌─────────────┐
                            Auto  │ Critical    │
                                  │ keywords?   │
                                  └─────────────┘
                                       │      │
                                      YES    NO
                                       │      │
                                       ▼      ▼
                                      P1    AI
                                     Auto  Analysis
                                            │
                                            ▼
                                   ┌──────────────┐
                                   │ P1/P2/P3/P4  │
                                   │ Normal Flow  │
                                   └──────────────┘
```

## Severity Level Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    SEVERITY LEVELS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  P1 (Critical) 🔴                                  SLA: 1 hour  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Production down                                              │
│  • All users affected                                           │
│  • Security breach                                              │
│  • 3rd follow-up                                                │
│  • Legal/cancellation threats                                   │
│  • Losing money/revenue                                         │
│                                                                  │
│  P2 (High) 🟡                                     SLA: 4 hours  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Major feature broken                                         │
│  • Blocking work                                                │
│  • Time-sensitive requests                                      │
│  • Frustrated customers                                         │
│  • Multiple exclamations                                        │
│                                                                  │
│  P3 (Medium) 🔵                                  SLA: 24 hours  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Minor bugs                                                   │
│  • Normal requests                                              │
│  • Workaround available                                         │
│  • "Fix when possible"                                          │
│                                                                  │
│  P4 (Low) 🟢                                     SLA: 72 hours  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Feature requests                                             │
│  • Suggestions                                                  │
│  • "Nice to have"                                               │
│  • Enhancement ideas                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
