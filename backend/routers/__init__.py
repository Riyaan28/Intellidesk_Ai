"""
Routers package initialization
"""

from routers.email_routes import router as emails_router
from routers.tickets import router as tickets_router
from routers.analytics import router as analytics_router

__all__ = ['emails_router', 'tickets_router', 'analytics_router']
