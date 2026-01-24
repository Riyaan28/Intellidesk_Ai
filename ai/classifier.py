"""
Smart Email Understanding Module
Strategy: Lightweight ML classifier with optional LLM fallback
Minimizes expensive LLM API calls while maintaining accuracy
"""

from typing import Dict, List
import time
import re

try:
    from .lightweight_classifier import lightweight_classifier
    from .ai_config import CONFIDENCE_HIGH, ENABLE_LLM_FALLBACK
except ImportError:
    from ai.lightweight_classifier import lightweight_classifier
    from ai.ai_config import CONFIDENCE_HIGH, ENABLE_LLM_FALLBACK


class EmailClassifier:
    """
    Smart Email Understanding Module
    
    Processing Pipeline:
    1. Spam detection (keyword-based) - Fast spam detection
    2. Lightweight Classifier (Calibrated TF-IDF + LogReg) - 80%+ accuracy
    3. LLM Fallback (optional, disabled by default) - Only if confidence < 0.80
    
    This strategy minimizes LLM API calls
    """
    
    # Spam keywords for quick detection
    SPAM_KEYWORDS = [
        'click here', 'free prize', 'limited time', 'claim now', 'verify account',
        'congratulations', 'winner', 'unsubscribe', 'act now', 'expires soon',
        'limited offer', 'special promotion', 'guaranteed', 'risk-free'
    ]
    
    LLM_THRESHOLD = CONFIDENCE_HIGH
    LLM_ENABLED = ENABLE_LLM_FALLBACK
    
    def __init__(self):
        pass
    
    def classify_email(self, subject: str, body: str, sender: str = "") -> Dict:
        """
        Classify email with smart routing strategy
        
        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address (optional)
        
        Returns:
            {
                'is_spam': bool,
                'category': str,
                'confidence': float,
                'method_used': str,
                'subcategory': str,
                'language_detected': list,
                'reasoning': str,
                'requires_review': bool,
                'processing_time_ms': float
            }
        """
        
        start_time = time.time()
        
        # STEP 1: Quick spam detection (keyword-based)
        is_spam, spam_confidence = self._detect_spam(subject, body)
        
        # If high-confidence spam, stop here
        if is_spam and spam_confidence > 0.90:
            processing_time = (time.time() - start_time) * 1000
            return {
                'is_spam': True,
                'category': 'Spam',
                'confidence': spam_confidence,
                'method_used': 'spam_filter',
                'subcategory': 'Promotional/Spam',
                'language_detected': ['English'],
                'reasoning': 'Spam keywords detected',
                'requires_review': False,
                'processing_time_ms': round(processing_time, 2)
            }
        
        # STEP 2: Lightweight ML Classification
        lightweight_result = lightweight_classifier.classify(subject, body)
        
        # If confidence >= threshold, accept result
        if lightweight_result['confidence'] >= self.LLM_THRESHOLD:
            processing_time = (time.time() - start_time) * 1000
            return {
                'is_spam': False,
                'category': lightweight_result['category'],
                'confidence': lightweight_result['confidence'],
                'method_used': 'lightweight_classifier',
                'subcategory': self._infer_subcategory(lightweight_result['category']),
                'language_detected': lightweight_result['language_detected'],
                'reasoning': f"High confidence: {lightweight_result['confidence']:.1%}",
                'requires_review': False,
                'processing_time_ms': round(processing_time, 2)
            }
        
        # STEP 3: Low confidence - flag for review (LLM disabled by default)
        processing_time = (time.time() - start_time) * 1000
        return {
            'is_spam': False,
            'category': lightweight_result['category'],
            'confidence': lightweight_result['confidence'],
            'method_used': 'lightweight_classifier_review',
            'subcategory': self._infer_subcategory(lightweight_result['category']),
            'language_detected': lightweight_result['language_detected'],
            'reasoning': f"Low confidence ({lightweight_result['confidence']:.1%}) - requires review",
            'requires_review': True,
            'processing_time_ms': round(processing_time, 2)
        }
    
    def _detect_spam(self, subject: str, body: str) -> tuple:
        """Quick spam detection using keywords"""
        text = f"{subject} {body}".lower()
        spam_count = sum(1 for keyword in self.SPAM_KEYWORDS if keyword in text)
        
        if spam_count >= 3:
            return True, 0.99
        elif spam_count >= 2:
            return True, 0.85
        else:
            return False, 0.0
    
    def _infer_subcategory(self, category: str) -> str:
        """
        Infer a reasonable subcategory based on main category
        (Lightweight classifier doesn't provide subcategories)
        """
        subcategory_map = {
            'Technical Support': 'Technical Issue',
            'Access Request': 'User Management',
            'Billing/Invoice': 'Payment',
            'Feature Request': 'Enhancement',
            'Hardware/Infrastructure': 'Infrastructure',
            'How-To/Documentation': 'Configuration',
            'Data Request': 'Data Export',
            'Complaint/Escalation': 'Service Issue',
            'General Inquiry': 'General'
        }
        return subcategory_map.get(category, 'General')
    
    def classify_batch(self, emails: List[Dict]) -> List[Dict]:
        """
        Classify multiple emails efficiently
        
        Args:
            emails: List of dicts with 'subject', 'body', 'sender' keys
        
        Returns:
            List of classification results with statistics
        """
        results = []
        stats = {
            'total': len(emails),
            'spam_filtered': 0,
            'lightweight_classified': 0,
            'llm_fallback': 0,
            'flagged_for_review': 0
        }
        
        for email in emails:
            result = self.classify_email(
                email.get('subject', ''),
                email.get('body', ''),
                email.get('sender', '')
            )
            results.append(result)
            
            # Track statistics
            if result['is_spam']:
                stats['spam_filtered'] += 1
            elif result['method_used'] == 'lightweight_classifier' and not result['requires_review']:
                stats['lightweight_classified'] += 1
            elif result.get('requires_review'):
                stats['flagged_for_review'] += 1
        
        return {
            'results': results,
            'statistics': stats,
            'llm_usage_percentage': round((stats['llm_fallback'] / stats['total']) * 100, 1)
        }


# Singleton instance
classifier = EmailClassifier()
