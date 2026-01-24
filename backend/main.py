"""
IntelliDesk AI - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import sys
import os
from datetime import datetime

# Add AI module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import API_TITLE, API_VERSION, API_DESCRIPTION, CORS_ORIGINS
from database import get_db, init_db
from routers import emails_router, tickets_router, analytics_router
from schemas import HealthCheck

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emails_router)
app.include_router(tickets_router)
app.include_router(analytics_router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    """
    print("🚀 Starting IntelliDesk AI Backend...")
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized")
    print(f"📡 API Documentation: http://localhost:8000/docs")


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": "IntelliDesk AI - The Perfect Response, Every Time",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["system"])
async def health_check(db: Session = Depends(get_db)):
    """
    System health check
    """
    # Check database
    db_status = "healthy"
    try:
        db.execute("SELECT 1")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check AI service
    ai_status = "healthy"
    try:
        from ai import classifier
        ai_status = "healthy" if classifier else "unavailable"
    except Exception as e:
        ai_status = f"unhealthy: {str(e)}"
    
    # Check vector DB
    vector_status = "healthy"
    try:
        from ai import embedding_service
        stats = embedding_service.get_stats()
        vector_status = f"healthy ({stats['total_tickets']} tickets indexed)"
    except Exception as e:
        vector_status = f"unhealthy: {str(e)}"
    
    overall_status = "healthy" if all(
        "healthy" in s for s in [db_status, ai_status, vector_status]
    ) else "degraded"
    
    return HealthCheck(
        status=overall_status,
        database=db_status,
        ai_service=ai_status,
        vector_db=vector_status,
        timestamp=datetime.utcnow()
    )


@app.get("/api/test-email", tags=["testing"])
async def test_email_processing(db: Session = Depends(get_db)):
    """
    Test endpoint with sample email
    """
    from .services.email_processor import EmailProcessor
    
    processor = EmailProcessor(db)
    
    sample_email = {
        "subject": "Urgent: App crashes when uploading files",
        "body": """Hi Support Team,

Our production app is crashing whenever users try to upload PDF files larger than 10MB. This is affecting all our users and blocking critical workflows.

Error message: "Error 500 - Internal Server Error"

This is URGENT! Please help ASAP!

Best regards,
John Smith
IT Manager
Tech Corp Inc.
john.smith@techcorp.com
+1-555-0123""",
        "sender": "john.smith@techcorp.com",
        "headers": {}
    }
    
    result = await processor.process_email(**sample_email)
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
