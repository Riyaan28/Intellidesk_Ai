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
        Detect urgency signals in email with comprehensive analysis
        """
        signals = []
        text = subject + " " + body
        text_lower = text.lower()
        
        # 1. TONE DETECTION
        # ALL CAPS detection - indicates anger/urgency
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len([c for c in text if c.isalpha()]), 1)
        if caps_ratio > 0.5:
            signals.append("ANGRY_TONE_HIGH_CAPS")
        elif caps_ratio > 0.3:
            signals.append("ELEVATED_TONE_CAPS")
        
        # Check for all caps words (specific angry expressions)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        if len(caps_words) >= 3:
            signals.append("MULTIPLE_CAPS_WORDS")
        
        # Exclamation marks - shows urgency/frustration
        exclamation_count = text.count('!')
        if exclamation_count >= 5:
            signals.append("VERY_HIGH_URGENCY_EXCLAMATIONS")
        elif exclamation_count >= 3:
            signals.append("HIGH_URGENCY_EXCLAMATIONS")
        
        # Emotional language detection
        frustrated_words = ['frustrated', 'unacceptable', 'disappointed', 'angry', 
                          'furious', 'ridiculous', 'terrible', 'horrible', 'worst']
        if any(word in text_lower for word in frustrated_words):
            signals.append("EMOTIONAL_LANGUAGE")
        
        # 2. TIME SENSITIVITY
        time_keywords = {
            'critical': ['immediately', 'right now', 'asap', 'urgent', 'emergency', 'now'],
            'high': ['today', 'this morning', 'this afternoon', 'within hours', 'very soon'],
            'medium': ['soon', 'quickly', 'prompt', 'expedite']
        }
        
        for urgency_level, keywords in time_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                signals.append(f"TIME_SENSITIVE_{urgency_level.upper()}")
                break
        
        # 3. BUSINESS IMPACT
        impact_keywords = {
            'revenue': ['losing money', 'revenue loss', 'financial impact', 'costing us', 
                       'sales down', 'lost revenue', 'money', 'cost'],
            'customers': ['customers waiting', 'customer complaints', 'all users', 
                         'everyone affected', 'clients impacted', 'users cannot'],
            'production': ['production down', 'system down', 'outage', 'offline', 
                          'not working', 'broken', 'crashed']
        }
        
        for impact_type, keywords in impact_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                signals.append(f"BUSINESS_IMPACT_{impact_type.upper()}")
        
        # 4. ESCALATION KEYWORDS
        escalation_detected = False
        for keyword in ESCALATION_KEYWORDS:
            if keyword in text_lower:
                signals.append(f"ESCALATION_KEYWORD_{keyword.upper()}")
                escalation_detected = True
        
        if escalation_detected:
            signals.append("ESCALATION_LANGUAGE")
        
        # 5. REPETITION (indicates frustration)
        repeated_phrases = re.findall(r'\b(\w+)\s+\1\b', text_lower)
        if len(repeated_phrases) >= 2:
            signals.append("REPETITION_FRUSTRATION")
        
        return signals
    
    def _has_critical_keywords(self, subject: str, body: str) -> bool:
        """
        Check for P1 critical keywords that require immediate response
        """
        text = (subject + " " + body).lower()
        
        critical_patterns = [
            # Production/System issues
            r'\ball users affected\b',
            r'\bproduction down\b',
            r'\bserver down\b',
            r'\bsystem down\b',
            r'\boutage\b',
            r'\bdown for everyone\b',
            r'\bcompletely broken\b',
            
            # Critical severity
            r'\bcritical issue\b',
            r'\bcritical bug\b',
            r'\bemergency\b',
            r'\bsevere\b',
            
            # Business impact
            r'\blosing money\b',
            r'\blosing revenue\b',
            r'\bcannot work\b',
            r'\bno one can\b',
            
            # Security
            r'\bsecurity breach\b',
            r'\bdata leak\b',
            r'\bhacked\b'
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
        
        # Use signal-based classification as primary method
        if len(signals) >= 3:
            # Multiple urgent signals = P1 or P2
            if any(s.startswith('BUSINESS_IMPACT') or s.startswith('ESCALATION') for s in signals):
                return self._create_urgency_result('P1', signals, reasoning='Multiple critical signals detected')
            return self._create_urgency_result('P2', signals, reasoning='Multiple urgency signals detected')
        elif len(signals) >= 1:
            # Some signals = P2 or P3
            if any(s.startswith('TIME_SENSITIVE_CRITICAL') or s.startswith('ANGRY_TONE') for s in signals):
                return self._create_urgency_result('P2', signals, reasoning='Time-sensitive or urgent tone detected')
            return self._create_urgency_result('P3', signals, reasoning='Minor urgency signals detected')
        
        # Fallback to AI for no clear signals
        prompt = f"""Classify this support ticket urgency. Respond with JSON only.

Subject: {subject}
Body: {body_truncated}
Category: {category}

RULES:
- P1 (Critical): Production down, security breach, all users affected, data loss
- P2 (High): Major feature broken, blocking multiple users, urgent requests
- P3 (Medium): Minor bugs, single user issues, normal requests
- P4 (Low): Feature requests, suggestions, questions, documentation

Be decisive. Most tickets are P3 or P4. Only use P1/P2 for genuine emergencies.

Respond ONLY with valid JSON:
{{"severity": "P1", "reasoning": "production system down"}}"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            import json
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result = json.loads(result_text)
            
            severity = result.get('severity', 'P4')  # Default to P4 for normal requests
            
            # Validate severity
            if severity not in ['P1', 'P2', 'P3', 'P4']:
                severity = 'P4'
            
            return self._create_urgency_result(severity, signals, reasoning=result.get('reasoning', ''))
            
        except Exception as e:
            # Intelligent fallback based on category and content
            text_lower = (subject + " " + body).lower()
            
            # Check for question words - likely P4
            if any(word in text_lower for word in ['how do i', 'can you', 'is it possible', 'would like', 'feature request']):
                return self._create_urgency_result('P4', signals, reasoning='General inquiry or feature request')
            
            # Check for problem words - likely P3
            if any(word in text_lower for word in ['not working', 'error', 'issue', 'problem', 'broken', 'bug']):
                return self._create_urgency_result('P3', signals, reasoning='Technical issue reported')
            
            # Default to P4 for unclear cases
            return self._create_urgency_result('P4', signals, reasoning='Normal priority request')
    
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
