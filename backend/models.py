"""
Database Models
SQLAlchemy ORM models for IntelliDesk
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from database import Base


class SeverityEnum(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TicketStatusEnum(str, enum.Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    WAITING_CUSTOMER = "Waiting on Customer"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class ResponseTypeEnum(str, enum.Enum):
    PERFECT_MATCH = "perfect_match"
    PARTIAL_MATCH = "partial_match"
    RESOLUTION_BASED = "resolution_based"
    ACKNOWLEDGMENT = "acknowledgment"


class Customer(Base):
    """
    Customer/Company model
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    tier = Column(String(50), default="Silver")  # Gold, Silver, Bronze
    account_id = Column(String(100), unique=True)
    is_trial = Column(Boolean, default=False)
    is_lead = Column(Boolean, default=False)
    
    # Relationships
    users = relationship("User", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    """
    End user model
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    role = Column(String(100))
    department = Column(String(100))
    phone = Column(String(50))
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    customer = relationship("Customer", back_populates="users")
    tickets = relationship("Ticket", back_populates="user")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    """
    Support Ticket model
    """
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Email info
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    sender = Column(String(255), nullable=False)
    message_id = Column(String(500))
    
    # Customer info
    customer_id = Column(Integer, ForeignKey("customers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Classification
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    classification_confidence = Column(Float)
    classification_reasoning = Column(Text)
    requires_review = Column(Boolean, default=False)
    
    # Urgency
    severity = Column(SQLEnum(SeverityEnum), nullable=False)
    severity_name = Column(String(50))
    urgency_signals = Column(JSON)  # List of detected signals
    urgency_reasoning = Column(Text)
    
    # SLA
    sla_hours = Column(Integer, nullable=False)
    sla_deadline = Column(DateTime(timezone=True), nullable=False)
    first_response_at = Column(DateTime(timezone=True))
    resolution_due = Column(DateTime(timezone=True))
    is_sla_breached = Column(Boolean, default=False)
    
    # Status
    status = Column(SQLEnum(TicketStatusEnum), default=TicketStatusEnum.NEW)
    assigned_to = Column(String(255))  # Team or person
    
    # Thread & Deduplication
    is_thread = Column(Boolean, default=False)
    parent_ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    thread_count = Column(Integer, default=0)
    
    # Follow-up tracking & Escalation
    followup_count = Column(Integer, default=0)  # Number of follow-ups from same sender
    is_escalated = Column(Boolean, default=False)  # Auto-escalated flag
    escalation_reason = Column(String(255))  # Why it was escalated
    escalation_time = Column(DateTime(timezone=True))  # When escalated
    
    # Resolution
    resolution = Column(Text)
    resolved_at = Column(DateTime(timezone=True))
    
    # AI Response
    ai_response_type = Column(SQLEnum(ResponseTypeEnum))
    ai_response_text = Column(Text)
    ai_response_confidence = Column(Float)
    ai_response_sent = Column(Boolean, default=False)
    auto_sent = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(JSON)  # List of tags
    internal_notes = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
    replies = relationship("Ticket", backref="parent", remote_side=[id])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmailLog(Base):
    """
    Email activity log
    """
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    email_type = Column(String(50))  # incoming, outgoing, auto_response
    sender = Column(String(255))
    recipient = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())


class Analytics(Base):
    """
    Analytics and metrics
    """
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Volumes
    total_emails = Column(Integer, default=0)
    total_tickets = Column(Integer, default=0)
    duplicates_prevented = Column(Integer, default=0)
    
    # Classification
    avg_classification_confidence = Column(Float)
    manual_review_count = Column(Integer, default=0)
    
    # Response
    auto_responses_sent = Column(Integer, default=0)
    avg_response_time_seconds = Column(Float)
    
    # SLA
    sla_met_count = Column(Integer, default=0)
    sla_breached_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
