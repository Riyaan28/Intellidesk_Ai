"""
AI Configuration for IntelliDesk
Gemini AI integration settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "models/gemini-2.5-flash"  # Fast and cost-effective
GEMINI_EMBEDDING_MODEL = "models/embedding-001"

# Toggle LLM fallback usage. Default off to minimize API calls and cost.
ENABLE_LLM_FALLBACK = os.getenv("ENABLE_LLM_FALLBACK", "false").lower() == "true"

# Classification Confidence Thresholds
CONFIDENCE_HIGH = 0.80
CONFIDENCE_MEDIUM = 0.60
AUTO_SEND_CONFIDENCE = 0.95

# Categories
EMAIL_CATEGORIES = [
    "Technical Support",
    "Access Request",
    "Billing/Invoice",
    "Feature Request",
    "Hardware/Infrastructure",
    "How-To/Documentation",
    "Data Request",
    "Complaint/Escalation",
    "General Inquiry"
]

# Severity Levels
SEVERITY_LEVELS = {
    "P1": {
        "name": "Critical",
        "sla_hours": 1,
        "keywords": ["urgent", "emergency", "down", "critical", "all users affected", "production", "outage"]
    },
    "P2": {
        "name": "High",
        "sla_hours": 4,
        "keywords": ["important", "priority", "blocking", "major", "broken", "not working"]
    },
    "P3": {
        "name": "Medium",
        "sla_hours": 24,
        "keywords": ["when possible", "convenience", "minor", "issue"]
    },
    "P4": {
        "name": "Low",
        "sla_hours": 72,
        "keywords": ["suggestion", "nice to have", "feature request", "enhancement"]
    }
}

# Escalation Keywords
ESCALATION_KEYWORDS = [
    "lawyer", "legal", "cancel", "refund", "unacceptable",
    "disappointed", "frustrated", "angry", "complaint"
]

# Deduplication Settings
SIMILARITY_THRESHOLD = 0.85
THREAD_WINDOW_HOURS = 72
SAME_SENDER_WINDOW_HOURS = 48

# Vector DB Settings
VECTOR_DB_PATH = "./faiss_index"
EMBEDDING_DIMENSION = 768
