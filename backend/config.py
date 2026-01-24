"""
Backend Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
API_TITLE = "IntelliDesk AI API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered email support automation system"

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://intellidesk:intellidesk123@localhost:5432/intellidesk"
)

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email Settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "support@intellidesk.ai")

# CORS
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000"
]

# Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Paths
AI_MODULE_PATH = "../ai"
