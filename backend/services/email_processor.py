"""
Email Processing Service
Core business logic for processing incoming emails
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import time
import re

# Add AI module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai import (
    classifier,
    urgency_detector,
    embedding_service,
    deduplication_service,
    auto_response_service
)

from models import Ticket, Customer, User
from schemas import (
    EmailProcessResponse,
    ClassificationResult,
    UrgencyResult,
    DeduplicationResult,
    AutoResponseResult
)
from sqlalchemy.orm import Session


class EmailProcessor:
    """
    Main email processing orchestrator
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_email(
        self,
        subject: str,
        body: str,
        sender: str,
        headers: Dict = None
    ) -> EmailProcessResponse:
        """
        Complete email processing pipeline
        
        Steps:
        1. Spam detection
        2. Classification
        3. Customer identification
        4. Deduplication check
        5. Urgency detection
        6. Ticket creation
        7. Auto-response generation
        """
        start_time = time.time()
        
        headers = headers or {}
        
        # 1. Email classification (includes spam detection)
        classification = classifier.classify_email(subject, body, sender)
        
        # Check if spam and return early
        if classification.get('is_spam', False):
            return self._create_spam_response(classification)
        
        # 2. Customer identification
        customer_info = await self._identify_customer(sender, body)
        
        # 3. Check follow-up count for sender (before deduplication)
        followup_count = self._count_recent_tickets(sender)
        is_followup = followup_count > 0
        
        # 4. Check for existing tickets (deduplication)
        existing_tickets = self._get_recent_tickets(sender)
        dedup_result = self._check_deduplication(
            headers,
            subject,
            body,
            sender,
            existing_tickets
        )
        
        # If duplicate, update existing ticket
        if dedup_result['is_duplicate']:
            ticket = self._update_existing_ticket(
                dedup_result['master_ticket_id'],
                subject,
                body
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return EmailProcessResponse(
                success=True,
                ticket_id=ticket.ticket_id,
                classification=ClassificationResult(**classification),
                urgency=UrgencyResult(
                    severity=ticket.severity,
                    severity_name=ticket.severity_name,
                    sla_hours=ticket.sla_hours,
                    sla_deadline=ticket.sla_deadline,
                    auto_escalate=False,
                    signals=[],
                    reasoning="Thread continuation"
                ),
                deduplication=DeduplicationResult(**dedup_result),
                auto_response=AutoResponseResult(
                    response_type="acknowledgment",
                    response_text="Added to existing ticket",
                    confidence=1.0,
                    auto_send=False,
                    references=[]
                ),
                customer_info=customer_info,
                processing_time_ms=processing_time
            )
        
        # 5. Urgency detection (with follow-up count for escalation)
        urgency = urgency_detector.detect_urgency(
            subject,
            body,
            classification['category'],
            is_followup=is_followup,
            followup_count=followup_count
        )
        
        # 6. Create ticket
        ticket = self._create_ticket(
            subject,
            body,
            sender,
            headers,
            classification,
            urgency,
            customer_info
        )
        
        # 7. Generate auto-response
        auto_response = auto_response_service.generate_response(
            subject,
            body,
            customer_info.get('name', sender.split('@')[0]),
            classification['category'],
            urgency['severity'],
            ticket.ticket_id,
            urgency['sla_hours']
        )
        
        # Update ticket with AI response
        ticket.ai_response_type = auto_response['response_type']
        ticket.ai_response_text = auto_response['response_text']
        ticket.ai_response_confidence = auto_response['confidence']
        
        # Auto-send if confidence is high
        if auto_response['auto_send']:
            # In production, send email here
            ticket.ai_response_sent = True
            ticket.auto_sent = True
            ticket.first_response_at = datetime.utcnow()
        
        self.db.commit()
        
        # Add to vector database for future similarity search
        embedding_service.add_ticket(
            ticket.ticket_id,
            subject,
            body,
            ""
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return EmailProcessResponse(
            success=True,
            ticket_id=ticket.ticket_id,
            classification=ClassificationResult(**classification),
            urgency=UrgencyResult(**urgency),
            deduplication=DeduplicationResult(**dedup_result),
            auto_response=AutoResponseResult(**auto_response),
            customer_info=customer_info,
            processing_time_ms=processing_time
        )
    
    async def _identify_customer(self, sender: str, body: str) -> Dict:
        """
        Identify customer from email domain and signature
        """
        domain = sender.split('@')[1] if '@' in sender else ''
        
        # Check if customer exists
        customer = self.db.query(Customer).filter(
            Customer.domain == domain
        ).first()
        
        if not customer:
            # New customer - create as lead
            company_name = self._extract_company_name(body, domain)
            customer = Customer(
                company_name=company_name or domain,
                domain=domain,
                tier="Silver",
                is_trial=True,
                is_lead=True,
                account_id=f"ACCT-{domain[:10].upper()}"
            )
            self.db.add(customer)
            self.db.commit()
        
        # Check if user exists
        user = self.db.query(User).filter(User.email == sender).first()
        
        if not user:
            # Extract user info from signature
            name, role, phone = self._extract_user_info(body, sender)
            user = User(
                customer_id=customer.id,
                email=sender,
                name=name,
                role=role,
                phone=phone
            )
            self.db.add(user)
            self.db.commit()
        
        return {
            'customer_id': customer.id,
            'user_id': user.id,
            'company_name': customer.company_name,
            'domain': domain,
            'tier': customer.tier,
            'is_trial': customer.is_trial,
            'is_lead': customer.is_lead,
            'name': user.name or sender.split('@')[0],
            'role': user.role,
            'phone': user.phone
        }
    
    def _extract_company_name(self, body: str, domain: str) -> Optional[str]:
        """
        Extract company name from email body or domain
        """
        # Try to extract from signature
        lines = body.split('\n')
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['regards', 'thanks', 'sincerely']):
                # Look at next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 3:
                        return lines[j].strip()
        
        # Fallback to domain
        return domain.split('.')[0].title()
    
    def _extract_user_info(self, body: str, email: str) -> tuple:
        """
        Extract user name, role, phone from email signature
        """
        name = email.split('@')[0].replace('.', ' ').title()
        role = None
        phone = None
        
        # Look for phone number
        phone_pattern = r'\+?\d[\d\s\-\(\)]{8,}\d'
        phone_match = re.search(phone_pattern, body)
        if phone_match:
            phone = phone_match.group(0)
        
        # Look for common role keywords in signature
        role_keywords = ['manager', 'director', 'engineer', 'analyst', 'developer', 'admin']
        for keyword in role_keywords:
            if keyword in body.lower():
                # Extract line containing role
                for line in body.split('\n'):
                    if keyword in line.lower():
                        role = line.strip()
                        break
                break
        
        return name, role, phone
    
    def _get_recent_tickets(self, sender: str, days: int = 3) -> List[Dict]:
        """
        Get recent tickets from same sender
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        tickets = self.db.query(Ticket).filter(
            Ticket.sender == sender,
            Ticket.created_at >= cutoff
        ).all()
        
        return [
            {
                'ticket_id': t.ticket_id,
                'subject': t.subject,
                'body': t.body,
                'sender': t.sender,
                'created_at': t.created_at,
                'message_id': t.message_id
            }
            for t in tickets
        ]
    
    def _count_recent_tickets(self, sender: str, days: int = 7) -> int:
        """
        Count recent tickets from same sender (for follow-up detection)
        Only count non-resolved tickets
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        count = self.db.query(Ticket).filter(
            Ticket.sender == sender,
            Ticket.created_at >= cutoff,
            Ticket.status.notin_(['Resolved', 'Closed'])
        ).count()
        
        return count
    
    def _check_deduplication(
        self,
        headers: Dict,
        subject: str,
        body: str,
        sender: str,
        existing_tickets: List[Dict]
    ) -> Dict:
        """
        Check for duplicate emails/threads
        """
        if not existing_tickets:
            return {'is_duplicate': False, 'master_ticket_id': None}
        
        match = deduplication_service.detect_thread(
            headers,
            subject,
            body,
            sender,
            existing_tickets
        )
        
        if match:
            return {
                'is_duplicate': True,
                'master_ticket_id': match['ticket_id'],
                'similarity_score': 1.0
            }
        
        return {'is_duplicate': False, 'master_ticket_id': None}
    
    def _create_ticket(
        self,
        subject: str,
        body: str,
        sender: str,
        headers: Dict,
        classification: Dict,
        urgency: Dict,
        customer_info: Dict
    ) -> Ticket:
        """
        Create new support ticket with follow-up tracking and escalation
        """
        # Generate ticket ID
        ticket_count = self.db.query(Ticket).count()
        ticket_id = f"TKT-{ticket_count + 1:06d}"
        
        # Count follow-ups (non-resolved tickets from this sender)
        followup_count = self._count_recent_tickets(sender)
        
        # Check if auto-escalated
        is_escalated = urgency.get('auto_escalate', False)
        escalation_reason = None
        escalation_time = None
        
        if is_escalated:
            escalation_time = datetime.utcnow()
            if followup_count >= 3:
                escalation_reason = f"Auto-escalated: {followup_count}rd follow-up"
            elif 'ESCALATION_LANGUAGE' in urgency.get('signals', []):
                escalation_reason = "Auto-escalated: Escalation keywords detected"
            else:
                escalation_reason = "Auto-escalated: Critical severity"
        
        ticket = Ticket(
            ticket_id=ticket_id,
            subject=subject,
            body=body,
            sender=sender,
            message_id=headers.get('Message-ID', ''),
            customer_id=customer_info['customer_id'],
            user_id=customer_info['user_id'],
            category=classification['category'],
            subcategory=classification.get('subcategory'),
            classification_confidence=classification['confidence'],
            classification_reasoning=classification.get('reasoning'),
            requires_review=classification['requires_review'],
            severity=urgency['severity'],
            severity_name=urgency['severity_name'],
            sla_hours=urgency['sla_hours'],
            sla_deadline=urgency['sla_deadline'],
            urgency_signals=urgency.get('signals', []),
            urgency_reasoning=urgency.get('reasoning'),
            status="New",
            is_thread=False,
            thread_count=0,
            followup_count=followup_count,
            is_escalated=is_escalated,
            escalation_reason=escalation_reason,
            escalation_time=escalation_time,
            created_at=datetime.utcnow()  # Explicitly set to current UTC time
        )
        
        self.db.add(ticket)
        self.db.flush()
        
        return ticket
    
    def _update_existing_ticket(
        self,
        ticket_id: str,
        subject: str,
        body: str
    ) -> Ticket:
        """
        Update existing ticket with new email
        """
        ticket = self.db.query(Ticket).filter(
            Ticket.ticket_id == ticket_id
        ).first()
        
        if ticket:
            ticket.thread_count += 1
            ticket.updated_at = datetime.utcnow()
            
            # Append to internal notes
            note = f"\n\n--- Follow-up ({datetime.utcnow()}) ---\n{subject}\n{body}"
            ticket.internal_notes = (ticket.internal_notes or "") + note
            
            self.db.commit()
        
        return ticket
    
    def _create_spam_response(self, classification: Dict) -> EmailProcessResponse:
        """
        Create response for spam emails
        """
        return EmailProcessResponse(
            success=False,
            ticket_id=None,
            classification=ClassificationResult(
                category="Spam",
                confidence=classification.get('confidence', 1.0),
                subcategory=classification.get('subcategory', 'Promotional'),
                requires_review=False,
                reasoning=classification.get('reasoning', 'Spam detected'),
                method_used=classification.get('method_used', 'spam_filter'),
                language_detected=classification.get('language_detected', ['English']),
                is_spam=True
            ),
            urgency=UrgencyResult(
                severity="P4",
                severity_name="Low",
                sla_hours=72,
                sla_deadline=datetime.utcnow(),
                auto_escalate=False,
                signals=["SPAM"],
                reasoning="Spam email"
            ),
            deduplication=DeduplicationResult(
                is_duplicate=False,
                master_ticket_id=None
            ),
            auto_response=AutoResponseResult(
                response_type="spam",
                response_text="Email filtered as spam",
                confidence=1.0,
                auto_send=False,
                references=[]
            ),
            customer_info=None,
            processing_time_ms=classification.get('processing_time_ms', 0.0)
        )
