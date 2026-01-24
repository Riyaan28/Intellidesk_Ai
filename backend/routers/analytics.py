"""
Analytics & Dashboard API Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any

from database import get_db
from models import Ticket, Customer
from schemas import DashboardStats, TicketResponse

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics and metrics
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    # Total tickets today
    total_today = db.query(Ticket).filter(
        Ticket.created_at >= today_start
    ).count()
    
    # Total tickets this week
    total_week = db.query(Ticket).filter(
        Ticket.created_at >= week_start
    ).count()
    
    # Average response time (in seconds)
    avg_response = db.query(
        func.avg(
            func.extract('epoch', Ticket.first_response_at - Ticket.created_at)
        )
    ).filter(
        Ticket.first_response_at.isnot(None)
    ).scalar() or 0
    
    # SLA compliance rate
    total_with_sla = db.query(Ticket).filter(
        Ticket.first_response_at.isnot(None)
    ).count()
    
    sla_met = db.query(Ticket).filter(
        Ticket.first_response_at.isnot(None),
        Ticket.is_sla_breached == False
    ).count()
    
    sla_rate = (sla_met / total_with_sla * 100) if total_with_sla > 0 else 0
    
    # Auto-response rate
    total_tickets = db.query(Ticket).count()
    auto_responses = db.query(Ticket).filter(
        Ticket.ai_response_sent == True
    ).count()
    
    auto_rate = (auto_responses / total_tickets * 100) if total_tickets > 0 else 0
    
    # Top categories
    top_categories = db.query(
        Ticket.category,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.category)\
     .order_by(desc('count'))\
     .limit(5)\
     .all()
    
    top_categories_list = [
        {"category": cat, "count": count}
        for cat, count in top_categories
    ]
    
    # Severity distribution
    severity_dist = db.query(
        Ticket.severity,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.severity).all()
    
    severity_dict = {
        severity: count
        for severity, count in severity_dist
    }
    
    # Recent tickets
    recent = db.query(Ticket)\
        .order_by(desc(Ticket.created_at))\
        .limit(10)\
        .all()
    
    recent_tickets = [TicketResponse.from_orm(t) for t in recent]
    
    return DashboardStats(
        total_tickets_today=total_today,
        total_tickets_week=total_week,
        avg_response_time=float(avg_response),
        sla_compliance_rate=float(sla_rate),
        auto_response_rate=float(auto_rate),
        top_categories=top_categories_list,
        severity_distribution=severity_dict,
        recent_tickets=recent_tickets
    )


@router.get("/trends")
async def get_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get ticket trends over time
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily ticket counts
    daily_counts = db.query(
        func.date(Ticket.created_at).label('date'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= start_date
    ).group_by(func.date(Ticket.created_at))\
     .order_by('date')\
     .all()
    
    # Category trends
    category_trends = db.query(
        func.date(Ticket.created_at).label('date'),
        Ticket.category,
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= start_date
    ).group_by(func.date(Ticket.created_at), Ticket.category)\
     .order_by('date')\
     .all()
    
    return {
        "daily_counts": [
            {"date": str(date), "count": count}
            for date, count in daily_counts
        ],
        "category_trends": [
            {"date": str(date), "category": cat, "count": count}
            for date, cat, count in category_trends
        ]
    }


@router.get("/performance")
async def get_performance_metrics(
    db: Session = Depends(get_db)
):
    """
    Get AI performance metrics
    """
    total = db.query(Ticket).count()
    
    # Classification confidence
    avg_confidence = db.query(
        func.avg(Ticket.classification_confidence)
    ).scalar() or 0
    
    # Manual review rate
    needs_review = db.query(Ticket).filter(
        Ticket.requires_review == True
    ).count()
    
    review_rate = (needs_review / total * 100) if total > 0 else 0
    
    # Auto-send success rate
    auto_sent = db.query(Ticket).filter(
        Ticket.auto_sent == True
    ).count()
    
    auto_rate = (auto_sent / total * 100) if total > 0 else 0
    
    # Deduplication stats
    threads = db.query(Ticket).filter(
        Ticket.is_thread == True
    ).count()
    
    # Response type distribution
    response_types = db.query(
        Ticket.ai_response_type,
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.ai_response_type.isnot(None)
    ).group_by(Ticket.ai_response_type).all()
    
    return {
        "total_tickets": total,
        "avg_classification_confidence": float(avg_confidence),
        "manual_review_rate": float(review_rate),
        "auto_response_rate": float(auto_rate),
        "threads_detected": threads,
        "response_type_distribution": {
            str(rtype): count
            for rtype, count in response_types
        }
    }
