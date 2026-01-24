"""
Urgency & Severity Detection Module
Determines P1-P4 priority levels with SLA assignment
"""

import google.generativeai as genai
import re
from typing import Dict
from datetime import datetime, timedelta
from .ai_config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SEVERITY_LEVELS,
    ESCALATION_KEYWORDS
)

genai.configure(api_key=GEMINI_API_KEY)


class UrgencyDetector:
    """
    Detects urgency and assigns severity levels (P1-P4)
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.severity_levels = SEVERITY_LEVELS
    
    def detect_urgency(
        self,
        subject: str,
        body: str,
        category: str,
        is_followup: bool = False,
        followup_count: int = 0
    ) -> Dict:
        """
        Detect urgency and assign severity level
        
        Args:
            subject: Email subject
            body: Email body
            category: Email category
            is_followup: Whether this is a follow-up email
            followup_count: Number of follow-ups (0 if first email)
            
        Returns:
            {
                'severity': str (P1-P4),
                'severity_name': str,
                'sla_hours': int,
                'sla_deadline': datetime,
                'auto_escalate': bool,
                'reasoning': str,
                'signals': List[str]
            }
        """
        
        # First check rule-based signals
        signals = self._detect_urgency_signals(subject, body)
        
        # Auto-escalate on 3rd follow-up
        if followup_count >= 3:
            return self._create_urgency_result(
                'P1',
                signals=['3rd follow-up - auto escalation'],
                auto_escalate=True
            )
        
        # Check for critical keywords
        if self._has_critical_keywords(subject, body):
            return self._create_urgency_result(
                'P1',
                signals=signals,
                auto_escalate=True
            )
        
        # Use AI for nuanced detection
        return self._ai_urgency_detection(subject, body, category, signals)
    
    def _detect_urgency_signals(self, subject: str, body: str) -> list:
        """
        Detect urgency signals in email
        """
        signals = []
        text = subject + " " + body
        
        # ALL CAPS detection
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            signals.append("HIGH_CAPS_RATIO")
        
        # Exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count >= 3:
            signals.append("MULTIPLE_EXCLAMATIONS")
        
        # Time sensitivity
        time_keywords = ['immediately', 'asap', 'urgent', 'emergency', 'now', 'today']
        if any(keyword in text.lower() for keyword in time_keywords):
            signals.append("TIME_SENSITIVE")
        
        # Business impact
        impact_keywords = ['losing money', 'revenue', 'customers waiting', 'production']
        if any(keyword in text.lower() for keyword in impact_keywords):
            signals.append("BUSINESS_IMPACT")
        
        # Escalation keywords
        if any(keyword in text.lower() for keyword in ESCALATION_KEYWORDS):
            signals.append("ESCALATION_LANGUAGE")
        
        return signals
    
    def _has_critical_keywords(self, subject: str, body: str) -> bool:
        """
        Check for P1 critical keywords
        """
        text = (subject + " " + body).lower()
        
        critical_patterns = [
            r'\ball users affected\b',
            r'\bproduction down\b',
            r'\bserver down\b',
            r'\boutage\b',
            r'\bcritical issue\b',
            r'\bemergency\b'
        ]
        
        return any(re.search(pattern, text) for pattern in critical_patterns)
    
    def _ai_urgency_detection(
        self,
        subject: str,
        body: str,
        category: str,
        signals: list
    ) -> Dict:
        """
        AI-based urgency detection for nuanced cases
        """
        
        body_truncated = body[:400] if len(body) > 400 else body
        
        prompt = f"""You are a support ticket urgency classifier.

Email Subject: {subject}
Email Body: {body_truncated}
Category: {category}
Detected Signals: {', '.join(signals)}

Severity Levels:
- P1 (Critical): Production down, all users affected, emergency (SLA: 1 hour)
- P2 (High): Major feature broken, blocking issue (SLA: 4 hours)
- P3 (Medium): Minor issue, workaround available (SLA: 24 hours)
- P4 (Low): Feature request, nice-to-have (SLA: 72 hours)

Respond ONLY in this JSON format:
{{
    "severity": "P1/P2/P3/P4",
    "reasoning": "brief explanation in 15 words or less"
}}"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            import json
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result = json.loads(result_text)
            
            severity = result.get('severity', 'P3')
            return self._create_urgency_result(severity, signals, reasoning=result.get('reasoning'))
            
        except Exception as e:
            # Default to P3 on error
            return self._create_urgency_result('P3', signals, reasoning='AI detection failed - defaulting to medium')
    
    def _create_urgency_result(
        self,
        severity: str,
        signals: list,
        auto_escalate: bool = False,
        reasoning: str = ""
    ) -> Dict:
        """
        Create urgency result dict
        """
        severity_info = self.severity_levels.get(severity, self.severity_levels['P3'])
        
        sla_deadline = datetime.utcnow() + timedelta(hours=severity_info['sla_hours'])
        
        return {
            'severity': severity,
            'severity_name': severity_info['name'],
            'sla_hours': severity_info['sla_hours'],
            'sla_deadline': sla_deadline,
            'auto_escalate': auto_escalate or (severity == 'P1'),
            'signals': signals,
            'reasoning': reasoning or f"Detected as {severity_info['name']} priority"
        }


# Singleton instance
urgency_detector = UrgencyDetector()
