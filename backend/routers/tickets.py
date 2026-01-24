"""
Tickets API Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime, timedelta

from database import get_db
from models import Ticket, Customer, User
from schemas import (
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    TicketStatusEnum,
    ResolveTicketRequest,
    ResolveTicketResponse
)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai.resolution_templates import generate_resolution_template
from ai.auto_reply import auto_response_service
from ai.test_ticket_generator import test_ticket_generator
from ai.classifier import classifier
from ai.urgency import urgency_analyzer
from ai.deduplication import deduplication_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("/", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TicketStatusEnum] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all tickets with filtering and pagination
    """
    query = db.query(Ticket)
    
    # Apply filters
    if status:
        query = query.filter(Ticket.status == status)
    
    if severity:
        query = query.filter(Ticket.severity == severity)
    
    if category:
        query = query.filter(Ticket.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Ticket.subject.ilike(search_term)) |
            (Ticket.body.ilike(search_term)) |
            (Ticket.ticket_id.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    tickets = query.order_by(desc(Ticket.created_at))\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return TicketListResponse(
        total=total,
        tickets=[TicketResponse.from_orm(t) for t in tickets],
        page=page,
        page_size=page_size
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed ticket information with related tickets
    Uses improved logic: same classification, >85% similarity within 72h
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get customer info
    customer = db.query(Customer).filter(Customer.id == ticket.customer_id).first()
    
    # Get related tickets using improved logic
    # Get all tickets with same classification
    all_tickets = db.query(Ticket).filter(
        Ticket.ticket_id != ticket_id,
        Ticket.category == ticket.category  # Same classification only
    ).all()
    
    existing_tickets = [
        {
            'ticket_id': t.ticket_id,
            'subject': t.subject,
            'body': t.body,
            'sender': t.sender,
            'category': t.category,
            'severity': t.severity,
            'created_at': t.created_at,
            'status': t.status
        }
        for t in all_tickets
    ]
    
    related_tickets = []
    
    # Use semantic similarity (>85% within 72 hours)
    from ai import embedding_service
    similar_tickets = embedding_service.search_similar(
        ticket.subject,
        ticket.body,
        top_k=5,
        threshold=0.85  # 85% as specified
    )
    
    # Filter by time window and same category
    for similar in similar_tickets:
        similar_id = similar.get('ticket_id')
        if similar_id and similar_id != ticket_id:
            similar_ticket = db.query(Ticket).filter(
                Ticket.ticket_id == similar_id,
                Ticket.category == ticket.category
            ).first()
            
            if similar_ticket:
                time_diff = datetime.utcnow() - similar_ticket.created_at
                if time_diff.total_seconds() / 3600 <= 72:  # Within 72 hours
                    related_tickets.append({
                        'ticket_id': similar_ticket.ticket_id,
                        'subject': similar_ticket.subject,
                        'similarity': similar.get('similarity', 0.0),
                        'category': similar_ticket.category,
                        'severity': similar_ticket.severity,
                        'status': similar_ticket.status
                    })
    
    # Build response
    response_data = TicketResponse.from_orm(ticket)
    detail_response = TicketDetailResponse(
        **response_data.dict(),
        customer_company=customer.company_name if customer else None,
        customer_tier=customer.tier if customer else None,
        similar_tickets=related_tickets[:3]  # Limit to top 3
    )
    
    return detail_response


@router.patch("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    status: TicketStatusEnum,
    resolution: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update ticket status
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = status
    
    if status == TicketStatusEnum.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
        if resolution:
            ticket.resolution = resolution
    
    db.commit()
    
    return {"success": True, "ticket_id": ticket_id, "status": status}


@router.post("/{ticket_id}/notes")
async def add_internal_note(
    ticket_id: str,
    note: str,
    db: Session = Depends(get_db)
):
    """
    Add internal note to ticket
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_note = f"\n[{timestamp}] {note}"
    ticket.internal_notes = (ticket.internal_notes or "") + new_note
    
    db.commit()
    
    return {"success": True, "ticket_id": ticket_id}


@router.get("/{ticket_id}/thread")
async def get_ticket_thread(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all emails in a ticket thread
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get all related tickets (parent + replies)
    related_tickets = []
    
    if ticket.parent_ticket_id:
        # Get parent
        parent = db.query(Ticket).filter(Ticket.id == ticket.parent_ticket_id).first()
        if parent:
            related_tickets.append(parent)
    
    # Get all replies
    replies = db.query(Ticket).filter(Ticket.parent_ticket_id == ticket.id).all()
    related_tickets.extend(replies)
    
    return {
        "ticket_id": ticket_id,
        "thread_count": len(related_tickets),
        "emails": [
            {
                "ticket_id": t.ticket_id,
                "subject": t.subject,
                "body": t.body,
                "sender": t.sender,
                "created_at": t.created_at
            }
            for t in sorted(related_tickets, key=lambda x: x.created_at)
        ]
    }


@router.get("/{ticket_id}/resolution-template")
async def get_resolution_template(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Get intelligent resolution template based on ticket category and tone
    
    Returns:
        Generated template text that is calm, polite, and category-specific
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Generate intelligent template
    template = generate_resolution_template(
        category=ticket.category,
        sender_name=ticket.sender,
        email_body=ticket.body,
        subject=ticket.subject
    )
    
    return {"template": template}


@router.get("/{ticket_id}/perfect-reply")
async def get_perfect_llm_reply(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate perfect LLM reply for ticket resolution
    Auto-sends if confidence > 90%
    
    Returns:
        {
            'reply_text': str,
            'should_auto_send': bool,
            'auto_sent': bool,
            'sender_name': str,
            'company_name': str
        }
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Generate perfect reply using LLM
    result = auto_response_service.generate_perfect_reply(
        subject=ticket.subject,
        body=ticket.body,
        sender_email=ticket.sender,
        category=ticket.category,
        severity=ticket.severity,
        confidence=ticket.classification_confidence or 0.0
    )
    
    # Auto-send if confidence > 90%
    auto_sent = False
    if result['should_auto_send'] and ticket.classification_confidence and ticket.classification_confidence > 0.90:
        try:
            # Send email automatically
            email_sent = await send_resolution_email(
                recipient=ticket.sender,
                subject=f"Re: {ticket.subject}",
                body=result['reply_text'],
                ticket_id=ticket_id
            )
            
            if email_sent:
                # Mark ticket as resolved
                ticket.status = TicketStatusEnum.RESOLVED
                ticket.resolved_at = datetime.utcnow()
                ticket.resolution = result['reply_text']
                ticket.first_response_at = ticket.first_response_at or datetime.utcnow()
                ticket.auto_responded = True
                
                db.commit()
                db.refresh(ticket)
                
                auto_sent = True
        except Exception as e:
            print(f"Auto-send failed: {e}")
    
    return {
        'reply_text': result['reply_text'],
        'should_auto_send': result['should_auto_send'],
        'auto_sent': auto_sent,
        'sender_name': result['sender_name'],
        'company_name': result['company_name'],
        'confidence': ticket.classification_confidence or 0.0
    }


@router.post("/{ticket_id}/resolve", response_model=ResolveTicketResponse)
async def resolve_ticket_with_email(
    ticket_id: str,
    request: ResolveTicketRequest,
    db: Session = Depends(get_db)
):
    """
    Send resolution email and mark ticket as resolved
    
    Args:
        ticket_id: Ticket ID to resolve
        request: Contains reply_text and recipient
        
    Returns:
        Success status and ticket details
    """
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if already resolved
    if ticket.status in [TicketStatusEnum.RESOLVED, TicketStatusEnum.CLOSED]:
        raise HTTPException(status_code=400, detail="Ticket is already resolved")
    
    try:
        # STEP 1: Send email
        # In production, integrate with actual email service (SMTP, SendGrid, etc.)
        # For now, we'll simulate email sending
        email_sent = await send_resolution_email(
            recipient=request.recipient,
            subject=f"Re: {ticket.subject}",
            body=request.reply_text,
            ticket_id=ticket_id
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=500, 
                detail="Failed to send email. Ticket not resolved."
            )
        
        # STEP 2: Mark ticket as resolved (only if email sent successfully)
        ticket.status = TicketStatusEnum.RESOLVED
        ticket.resolved_at = datetime.utcnow()
        ticket.resolution = request.reply_text
        ticket.first_response_at = ticket.first_response_at or datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        return ResolveTicketResponse(
            success=True,
            ticket_id=ticket_id,
            status="Resolved",
            email_sent=True,
            recipient=request.recipient,
            resolved_at=ticket.resolved_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve ticket: {str(e)}"
        )


async def send_resolution_email(recipient: str, subject: str, body: str, ticket_id: str) -> bool:
    """
    Send resolution email to customer
    
    In production, integrate with:
    - SMTP (smtplib)
    - SendGrid
    - AWS SES
    - Mailgun
    - etc.
    
    For now, this simulates email sending and logs to console.
    """
    try:
        # Simulate email sending
        print("\n" + "="*80)
        print("📧 RESOLUTION EMAIL (Simulated)")
        print("="*80)
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Ticket ID: {ticket_id}")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
        
        # In production, add actual email sending here:
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = 'support@yourcompany.com'
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('your_email@gmail.com', 'your_password')
            server.send_message(msg)
        """
        
        # Return True to simulate successful send
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False


@router.delete("/clear-all")
async def clear_all_tickets(db: Session = Depends(get_db)):
    """
    Delete all tickets from the database
    
    Returns:
        {
            'success': bool,
            'deleted_count': int
        }
    """
    try:
        # Count tickets before deletion
        ticket_count = db.query(Ticket).count()
        
        # Delete all tickets
        db.query(Ticket).delete()
        db.commit()
        
        return {
            'success': True,
            'deleted_count': ticket_count,
            'message': f'Successfully deleted {ticket_count} ticket(s)'
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete tickets: {str(e)}"
        )


@router.post("/generate-test-tickets")
async def generate_test_tickets(
    count: int = Query(7, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Generate random test tickets for testing purposes
    
    Args:
        count: Number of tickets to generate (default: 7, max: 20)
        
    Returns:
        List of created ticket IDs
    """
    try:
        # Generate random test tickets
        test_tickets = test_ticket_generator.generate_random_tickets(count)
        
        created_tickets = []
        
        for ticket_data in test_tickets:
            # Classify the ticket
            classification = classifier.classify(
                ticket_data['subject'],
                ticket_data['body']
            )
            
            # Analyze urgency
            urgency_result = urgency_analyzer.analyze_urgency(
                ticket_data['subject'],
                ticket_data['body'],
                ticket_data['sender']
            )
            
            # Generate ticket ID
            ticket_id = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{db.query(Ticket).count() + 1:04d}"
            
            # Create ticket
            ticket = Ticket(
                ticket_id=ticket_id,
                subject=ticket_data['subject'],
                body=ticket_data['body'],
                sender=ticket_data['sender'],
                category=classification['category'],
                severity=urgency_result['severity'],
                urgency_signals=urgency_result.get('signals', []),
                classification_confidence=classification.get('confidence', 0.0),
                created_at=ticket_data['created_at'],
                status='Open'
            )
            
            db.add(ticket)
            db.flush()
            
            created_tickets.append({
                'ticket_id': ticket_id,
                'subject': ticket_data['subject'],
                'category': classification['category'],
                'severity': urgency_result['severity']
            })
        
        db.commit()
        
        return {
            'success': True,
            'count': len(created_tickets),
            'tickets': created_tickets,
            'message': f'Successfully created {len(created_tickets)} test ticket(s)'
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate test tickets: {str(e)}"
        )


@router.get("/{ticket_id}/related")
async def get_related_tickets(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Get related tickets using improved deduplication logic:
    - Same classification only
    - Embeddings similarity >85% within 72 hours
    - Fuzzy subject matching (ignoring Re:, timestamps)
    - Ticket reference parsing
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get all tickets from database
    all_tickets = db.query(Ticket).filter(
        Ticket.ticket_id != ticket_id,
        Ticket.category == ticket.category  # Same classification only
    ).all()
    
    # Convert to dict format
    existing_tickets = [
        {
            'ticket_id': t.ticket_id,
            'subject': t.subject,
            'body': t.body,
            'sender': t.sender,
            'category': t.category,
            'severity': t.severity,
            'created_at': t.created_at,
            'status': t.status
        }
        for t in all_tickets
    ]
    
    related_tickets = []
    
    # Method 1: Check ticket references in current ticket
    ticket_ref_match = deduplication_service._check_ticket_references(
        ticket.subject,
        ticket.body,
        existing_tickets
    )
    if ticket_ref_match:
        related_tickets.append(ticket_ref_match)
    
    # Method 2: Same sender within 48 hours
    sender_matches = [
        t for t in existing_tickets
        if t['sender'].lower() == ticket.sender.lower()
        and deduplication_service._within_time_window(t, 48)
        and deduplication_service._fuzzy_match(
            deduplication_service._normalize_subject(ticket.subject),
            deduplication_service._normalize_subject(t['subject'])
        )
    ]
    related_tickets.extend(sender_matches)
    
    # Method 3: Semantic similarity (>85% within 72 hours)
    from ai import embedding_service
    similar_tickets = embedding_service.search_similar(
        ticket.subject,
        ticket.body,
        top_k=5,
        threshold=0.85  # 85% similarity
    )
    
    # Filter by time window and same category
    for similar in similar_tickets:
        similar_id = similar.get('ticket_id')
        if similar_id and similar_id != ticket_id:
            similar_ticket = db.query(Ticket).filter(
                Ticket.ticket_id == similar_id,
                Ticket.category == ticket.category  # Same classification
            ).first()
            
            if similar_ticket:
                time_diff = datetime.utcnow() - similar_ticket.created_at
                if time_diff.total_seconds() / 3600 <= 72:  # Within 72 hours
                    related_tickets.append({
                        'ticket_id': similar_ticket.ticket_id,
                        'subject': similar_ticket.subject,
                        'body': similar_ticket.body,
                        'sender': similar_ticket.sender,
                        'category': similar_ticket.category,
                        'severity': similar_ticket.severity,
                        'created_at': similar_ticket.created_at,
                        'status': similar_ticket.status,
                        'similarity': similar.get('similarity', 0.0)
                    })
    
    # Remove duplicates
    seen_ids = set()
    unique_related = []
    for t in related_tickets:
        tid = t.get('ticket_id')
        if tid and tid not in seen_ids:
            seen_ids.add(tid)
            unique_related.append(t)
    
    return {
        'ticket_id': ticket_id,
        'related_count': len(unique_related),
        'related_tickets': unique_related[:10]  # Limit to 10
    }

