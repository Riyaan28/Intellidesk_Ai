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
    TicketStatusEnum
)

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
    Get detailed ticket information
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get customer info
    customer = db.query(Customer).filter(Customer.id == ticket.customer_id).first()
    
    # Get similar tickets using embeddings
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from ai import embedding_service
    
    similar_tickets = embedding_service.search_similar(
        ticket.subject,
        ticket.body,
        top_k=3,
        threshold=0.70
    )
    
    # Build response
    response_data = TicketResponse.from_orm(ticket)
    detail_response = TicketDetailResponse(
        **response_data.dict(),
        customer_company=customer.company_name if customer else None,
        customer_tier=customer.tier if customer else None,
        similar_tickets=similar_tickets
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
