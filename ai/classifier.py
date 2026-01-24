"""
Email Classification Module using Gemini AI
Classifies emails into predefined categories with confidence scores
"""

import google.generativeai as genai
from typing import Dict, List, Tuple, Optional
import re

try:
    from .ai_config import (
        GEMINI_API_KEY,
        GEMINI_MODEL,
        EMAIL_CATEGORIES,
        CONFIDENCE_HIGH
    )
except ImportError:
    from ai_config import (
        GEMINI_API_KEY,
        GEMINI_MODEL,
        EMAIL_CATEGORIES,
        CONFIDENCE_HIGH
    )

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


class EmailClassifier:
    """
    Classifies support emails into categories using Gemini AI
    Optimized to minimize API calls
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.categories = EMAIL_CATEGORIES
        
    def classify_email(self, subject: str, body: str, sender: str = "") -> Dict:
        """
        Classify email into category with confidence score
        
        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address
            
        Returns:
            {
                'category': str,
                'confidence': float,
                'subcategory': str,
                'requires_review': bool,
                'reasoning': str
            }
        """
        
        # First, try rule-based classification for obvious cases
        rule_result = self._rule_based_classification(subject, body)
        if rule_result and rule_result['confidence'] >= CONFIDENCE_HIGH:
            return rule_result
        
        # Use Gemini for complex cases
        return self._ai_classification(subject, body, sender)
    
    def _rule_based_classification(self, subject: str, body: str) -> Dict:
        """
        Fast rule-based classification for obvious patterns
        Reduces API calls by ~40%
        """
        
        text = (subject + " " + body).lower()
        
        # Billing patterns
        if any(word in text for word in ['invoice', 'payment', 'billing', 'subscription', 'charge']):
            return {
                'category': 'Billing/Invoice',
                'confidence': 0.85,
                'subcategory': 'Payment',
                'requires_review': False,
                'reasoning': 'Rule-based: Billing keywords detected'
            }
        
        # Access Request patterns
        if any(word in text for word in ['access', 'permission', 'admin rights', 'create user', 'add user']):
            return {
                'category': 'Access Request',
                'confidence': 0.85,
                'subcategory': 'User Management',
                'requires_review': False,
                'reasoning': 'Rule-based: Access request keywords detected'
            }
        
        # Technical Support - error codes
        if re.search(r'error\s*\d+|exception|crash|bug|not working', text, re.IGNORECASE):
            return {
                'category': 'Technical Support',
                'confidence': 0.82,
                'subcategory': 'Error/Bug',
                'requires_review': False,
                'reasoning': 'Rule-based: Error/crash keywords detected'
            }
        
        # How-to questions
        if any(word in text for word in ['how to', 'how do i', 'configure', 'setup', 'tutorial']):
            return {
                'category': 'How-To/Documentation',
                'confidence': 0.80,
                'subcategory': 'Configuration',
                'requires_review': False,
                'reasoning': 'Rule-based: How-to question detected'
            }
        
        return None
    
    def _ai_classification(self, subject: str, body: str, sender: str) -> Dict:
        """
        AI-based classification using Gemini for complex cases
        """
        
        # Truncate body to reduce tokens (keep first 500 chars)
        body_truncated = body[:500] if len(body) > 500 else body
        
        prompt = f"""You are an expert email classifier for a B2B SaaS support system.

Email Subject: {subject}
Email Body: {body_truncated}
Sender: {sender}

Categories:
1. Technical Support - App crashes, errors, bugs, technical issues
2. Access Request - User access, permissions, admin rights
3. Billing/Invoice - Payment, invoices, subscription issues
4. Feature Request - New features, enhancements
5. Hardware/Infrastructure - Server issues, hardware problems
6. How-To/Documentation - Configuration help, tutorials
7. Data Request - Export data, reports
8. Complaint/Escalation - Complaints, urgent escalations
9. General Inquiry - General questions, business hours

Analyze and respond ONLY in this exact JSON format:
{{
    "category": "exact category name from list above",
    "confidence": 0.XX (number between 0 and 1),
    "subcategory": "specific sub-topic",
    "reasoning": "brief explanation in 10 words"
}}"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            import json
            # Remove markdown code blocks if present
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result = json.loads(result_text)
            
            result['requires_review'] = result['confidence'] < CONFIDENCE_HIGH
            
            return result
            
        except Exception as e:
            # Fallback to General Inquiry on error
            return {
                'category': 'General Inquiry',
                'confidence': 0.50,
                'subcategory': 'Uncategorized',
                'requires_review': True,
                'reasoning': f'Classification error: {str(e)[:30]}'
            }
    
    def classify_batch(self, emails: List[Dict]) -> List[Dict]:
        """
        Classify multiple emails efficiently
        
        Args:
            emails: List of dicts with 'subject', 'body', 'sender'
            
        Returns:
            List of classification results
        """
        results = []
        for email in emails:
            result = self.classify_email(
                email.get('subject', ''),
                email.get('body', ''),
                email.get('sender', '')
            )
            results.append(result)
        
        return results
    
    def is_spam(self, subject: str, body: str) -> bool:
        """
        Detect spam/promotional emails
        
        Returns:
            True if spam, False otherwise
        """
        text = (subject + " " + body).lower()
        
        spam_indicators = [
            'unsubscribe',
            'click here to buy',
            'limited time offer',
            'act now',
            'congratulations you won',
            'nigerian prince',
            'inherit million',
            'viagra',
            'casino'
        ]
        
        spam_score = sum(1 for indicator in spam_indicators if indicator in text)
        
        return spam_score >= 2


# Singleton instance
classifier = EmailClassifier()
