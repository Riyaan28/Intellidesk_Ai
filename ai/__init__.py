"""
AI Module - IntelliDesk
Exposes all AI/NLP services
"""

from .classifier import classifier, EmailClassifier
from .urgency import urgency_detector, UrgencyDetector
from .embeddings import embedding_service, EmbeddingService
from .deduplication import deduplication_service, DeduplicationService
from .auto_reply import auto_response_service, AutoResponseService
from .ai_config import *

__all__ = [
    'classifier',
    'urgency_detector',
    'embedding_service',
    'deduplication_service',
    'auto_response_service',
    'EmailClassifier',
    'UrgencyDetector',
    'EmbeddingService',
    'DeduplicationService',
    'AutoResponseService'
]
