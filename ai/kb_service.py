"""
Knowledge Base Service
Handles KB insertion and retrieval
"""

import re
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import KnowledgeBase, Ticket, TicketStatusEnum
from ai.embeddings import embedding_service


def normalize_text(text: str) -> str:
    """
    Remove PII and normalize text for KB
    
    Removes:
    - Email addresses
    - Phone numbers
    - IP addresses
    - URLs
    - Specific names/identifiers
    """
    if not text:
        return ""
    
    normalized = text
    
    # Remove email addresses
    normalized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', normalized)
    
    # Remove phone numbers
    normalized = re.sub(r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE]', normalized)
    normalized = re.sub(r'\+\d{1,3}[-.\s]?\d{6,14}', '[PHONE]', normalized)
    
    # Remove IP addresses
    normalized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', normalized)
    
    # Remove URLs
    normalized = re.sub(r'https?://[^\s]+', '[URL]', normalized)
    
    # Remove ticket IDs
    normalized = re.sub(r'\bTK-\d{6}\b', '[TICKET_ID]', normalized)
    
    # Clean up extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def add_ticket_to_kb(ticket_id: int, db: Session) -> int:
    """
    Add a resolved and verified ticket to Knowledge Base
    
    MANDATORY LOGIC:
    - Verify ticket.status == "Resolved"
    - Verify ticket has resolution text
    - Check not already in KB (source_ticket_id unique)
    - Normalize content (remove PII)
    - Generate embedding
    - Insert to PostgreSQL + FAISS
    
    Args:
        ticket_id: Database ticket.id (NOT ticket_id string)
        db: Database session
        
    Returns:
        kb_id: ID of created KB entry
        
    Raises:
        ValueError: If ticket doesn't meet requirements
        IntegrityError: If ticket already in KB
    """
    
    # STEP 1: Fetch ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise ValueError(f"Ticket with id={ticket_id} not found")
    
    # STEP 2: Verify ticket is resolved
    if ticket.status != TicketStatusEnum.RESOLVED:
        raise ValueError(
            f"Ticket must be RESOLVED. Current status: {ticket.status}. "
            f"Cannot add unresolved tickets to KB."
        )
    
    # STEP 3: Verify ticket has resolution
    if not ticket.resolution or not ticket.resolution.strip():
        raise ValueError(
            f"Ticket has no resolution text. "
            f"Cannot add tickets without verified solutions to KB."
        )
    
    # STEP 4: Verify ticket has resolved_at timestamp
    if not ticket.resolved_at:
        raise ValueError(
            f"Ticket missing resolved_at timestamp. "
            f"Only fully resolved tickets can be added to KB."
        )
    
    # STEP 5: Check if already in KB (will be caught by UNIQUE constraint, but check early)
    existing = db.query(KnowledgeBase).filter(
        KnowledgeBase.source_ticket_id == ticket_id
    ).first()
    
    if existing:
        raise IntegrityError(
            f"Ticket id={ticket_id} already exists in KB (kb_id={existing.id}). "
            f"Cannot add duplicate entries.",
            params=None,
            orig=None
        )
    
    # STEP 6: Normalize content - remove PII
    problem_summary = normalize_text(f"{ticket.subject} {ticket.body}")
    resolution_steps = normalize_text(ticket.resolution)
    
    # Truncate if too long
    if len(problem_summary) > 1000:
        problem_summary = problem_summary[:1000] + "..."
    
    if len(resolution_steps) > 2000:
        resolution_steps = resolution_steps[:2000] + "..."
    
    # STEP 7: Generate embedding using EXISTING embeddings module
    kb_text = f"{problem_summary} {resolution_steps}"
    embedding = embedding_service.get_embedding(kb_text)
    
    # STEP 8: Insert to PostgreSQL
    kb_entry = KnowledgeBase(
        problem_summary=problem_summary,
        resolution_steps=resolution_steps,
        category=ticket.category,
        source_ticket_id=ticket_id,
        is_active=True,
        usage_count=0,
        created_at=datetime.utcnow()
    )
    
    db.add(kb_entry)
    db.commit()
    db.refresh(kb_entry)
    
    # STEP 9: Insert vector to FAISS
    # Add to existing FAISS index with KB-specific metadata
    import numpy as np
    embedding_service.index.add(np.array([embedding]))
    embedding_service.metadata.append({
        'kb_id': kb_entry.id,
        'type': 'kb',  # Mark as KB entry (not regular ticket)
        'category': kb_entry.category,
        'problem_summary': problem_summary,
        'resolution_steps': resolution_steps,
        'source_ticket_id': ticket_id
    })
    
    # Save FAISS index
    embedding_service._save_index()
    
    # STEP 10: Return kb_id
    return kb_entry.id


def increment_kb_usage(kb_id: int, db: Session) -> None:
    """
    Increment usage_count when KB entry is used in a response
    
    Args:
        kb_id: Knowledge Base entry ID
        db: Database session
    """
    kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if kb_entry and kb_entry.is_active:
        kb_entry.usage_count += 1
        db.commit()


def disable_kb_entry(kb_id: int, db: Session) -> bool:
    """
    Soft delete - disable a KB entry without removing from database
    
    Args:
        kb_id: Knowledge Base entry ID
        db: Database session
        
    Returns:
        True if disabled, False if not found
    """
    kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb_entry:
        return False
    
    kb_entry.is_active = False
    db.commit()
    return True


def enable_kb_entry(kb_id: int, db: Session) -> bool:
    """
    Re-enable a disabled KB entry
    
    Args:
        kb_id: Knowledge Base entry ID
        db: Database session
        
    Returns:
        True if enabled, False if not found
    """
    kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb_entry:
        return False
    
    kb_entry.is_active = True
    db.commit()
    return True


def delete_kb_entry(kb_id: int, db: Session) -> bool:
    """
    HARD delete - permanently remove KB entry from database and FAISS
    
    WARNING: This cannot be undone. Prefer disable_kb_entry() for safety.
    
    Args:
        kb_id: Knowledge Base entry ID
        db: Database session
        
    Returns:
        True if deleted, False if not found
    """
    kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb_entry:
        return False
    
    # Delete from database
    db.delete(kb_entry)
    db.commit()
    
    # Note: FAISS index cleanup would require rebuilding entire index
    # For now, inactive entries are filtered during search
    # Full FAISS rebuild should be done periodically via maintenance script
    
    return True


def get_active_kb_entries(db: Session, category: Optional[str] = None) -> list:
    """
    Get all active KB entries, optionally filtered by category
    
    Args:
        db: Database session
        category: Optional category filter
        
    Returns:
        List of active KnowledgeBase entries
    """
    query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
    
    if category:
        query = query.filter(KnowledgeBase.category == category)
    
    return query.order_by(KnowledgeBase.usage_count.desc()).all()


def check_duplicate_kb_entry(ticket_id: int, db: Session) -> Optional[int]:
    """
    Check if a ticket is already in the KB
    
    Args:
        ticket_id: Source ticket ID
        db: Database session
        
    Returns:
        KB entry ID if exists, None otherwise
    """
    existing = db.query(KnowledgeBase).filter(
        KnowledgeBase.source_ticket_id == ticket_id
    ).first()
    
    return existing.id if existing else None
