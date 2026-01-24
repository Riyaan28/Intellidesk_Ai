"""
Pydantic Schemas for API Request/Response
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityEnum(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TicketStatusEnum(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    WAITING_CUSTOMER = "Waiting on Customer"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


# Email Processing Schemas
class EmailProcessRequest(BaseModel):
    """
    Request to process an incoming email
    """
    subject: str
    body: str
    sender: EmailStr
    headers: Optional[Dict[str, str]] = {}
    received_at: Optional[datetime] = None


class ClassificationResult(BaseModel):
    """
    Email classification result
    """
    category: str
    confidence: float
    subcategory: Optional[str] = None
    requires_review: bool
    reasoning: str


class UrgencyResult(BaseModel):
    """
    Urgency detection result
    """
    severity: SeverityEnum
    severity_name: str
    sla_hours: int
    sla_deadline: datetime
    auto_escalate: bool
    signals: List[str]
    reasoning: str


class DeduplicationResult(BaseModel):
    """
    Deduplication check result
    """
    is_duplicate: bool
    master_ticket_id: Optional[str] = None
    similarity_score: Optional[float] = None


class AutoResponseResult(BaseModel):
    """
    Auto-response generation result
    """
    response_type: str
    response_text: str
    confidence: float
    auto_send: bool
    references: List[str] = []


class EmailProcessResponse(BaseModel):
    """
    Complete email processing result
    """
    success: bool
    ticket_id: Optional[str] = None
    classification: ClassificationResult
    urgency: UrgencyResult
    deduplication: DeduplicationResult
    auto_response: AutoResponseResult
    customer_info: Optional[Dict] = None
    processing_time_ms: float


# Ticket Schemas
class TicketBase(BaseModel):
    """
    Base ticket schema
    """
    subject: str
    body: str
    sender: EmailStr
    category: str
    severity: SeverityEnum


class TicketCreate(TicketBase):
    """
    Create ticket request
    """
    pass


class TicketResponse(TicketBase):
    """
    Ticket response
    """
    id: int
    ticket_id: str
    status: TicketStatusEnum
    sla_deadline: datetime
    created_at: datetime
    classification_confidence: float
    ai_response_text: Optional[str] = None
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """
    List of tickets response
    """
    total: int
    tickets: List[TicketResponse]
    page: int
    page_size: int


class TicketDetailResponse(TicketResponse):
    """
    Detailed ticket information
    """
    subcategory: Optional[str] = None
    classification_reasoning: Optional[str] = None
    urgency_signals: Optional[List[str]] = None
    urgency_reasoning: Optional[str] = None
    customer_company: Optional[str] = None
    customer_tier: Optional[str] = None
    thread_count: int = 0
    similar_tickets: List[Dict] = []
    
    class Config:
        from_attributes = True


# Customer Schemas
class CustomerBase(BaseModel):
    """
    Base customer schema
    """
    company_name: str
    domain: str
    tier: str = "Silver"


class CustomerCreate(CustomerBase):
    """
    Create customer request
    """
    pass


class CustomerResponse(CustomerBase):
    """
    Customer response
    """
    id: int
    account_id: Optional[str] = None
    is_trial: bool = False
    is_lead: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class DashboardStats(BaseModel):
    """
    Dashboard statistics
    """
    total_tickets_today: int
    total_tickets_week: int
    avg_response_time: float
    sla_compliance_rate: float
    auto_response_rate: float
    top_categories: List[Dict[str, Any]]
    severity_distribution: Dict[str, int]
    recent_tickets: List[TicketResponse]


# System Schemas
class HealthCheck(BaseModel):
    """
    System health check
    """
    status: str
    database: str
    ai_service: str
    vector_db: str
    timestamp: datetime
