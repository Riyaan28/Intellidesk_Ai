"""
Email Processing API Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import EmailProcessRequest, EmailProcessResponse
from services.email_processor import EmailProcessor

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.post("/process", response_model=EmailProcessResponse)
async def process_email(
    request: EmailProcessRequest,
    db: Session = Depends(get_db)
):
    """
    Process incoming email
    
    - **subject**: Email subject line
    - **body**: Email body content
    - **sender**: Sender email address
    - **headers**: Optional email headers
    """
    processor = EmailProcessor(db)
    
    try:
        result = await processor.process_email(
            subject=request.subject,
            body=request.body,
            sender=request.sender,
            headers=request.headers or {}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-process")
async def batch_process_emails(
    emails: List[EmailProcessRequest],
    db: Session = Depends(get_db)
):
    """
    Process multiple emails in batch
    """
    processor = EmailProcessor(db)
    results = []
    
    for email in emails:
        try:
            result = await processor.process_email(
                subject=email.subject,
                body=email.body,
                sender=email.sender,
                headers=email.headers or {}
            )
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "sender": email.sender
            })
    
    return {
        "total": len(emails),
        "processed": len(results),
        "results": results
    }
