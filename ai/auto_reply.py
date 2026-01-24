"""
Intelligent Auto-Response Module
Generates context-aware responses using Gemini AI
"""

import google.generativeai as genai
from typing import Dict, List, Optional
from .embeddings import embedding_service
from .ai_config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    AUTO_SEND_CONFIDENCE
)

genai.configure(api_key=GEMINI_API_KEY)


class AutoResponseService:
    """
    Generates intelligent auto-responses based on:
    - FAQ database
    - Past resolved tickets
    - Category and urgency
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.embedding_service = embedding_service
        self.faq_database = self._load_faq_database()
    
    def _load_faq_database(self) -> List[Dict]:
        """
        Load FAQ database
        In production, this would load from database
        """
        return [
            {
                'question': 'How do I reset my password?',
                'answer': 'To reset your password:\n1. Go to login page\n2. Click "Forgot Password"\n3. Enter your email\n4. Check your email for reset link\n5. Click link and set new password',
                'category': 'Access Request',
                'video_link': 'https://help.example.com/videos/reset-password',
                'manual_link': 'https://help.example.com/docs/password-reset'
            },
            {
                'question': 'App crashes on startup',
                'answer': 'Try these troubleshooting steps:\n1. Clear browser cache (Ctrl+Shift+Delete)\n2. Disable browser extensions\n3. Try incognito mode\n4. Update your browser to latest version\n5. If issue persists, contact support with error details',
                'category': 'Technical Support',
                'success_rate': '85%',
                'avg_resolution_time': '15 minutes'
            },
            {
                'question': 'How to export data to Excel?',
                'answer': 'To export data:\n1. Navigate to Reports section\n2. Select desired date range and filters\n3. Click "Export" button in top-right\n4. Choose "Excel (.xlsx)" format\n5. Download will start automatically',
                'category': 'How-To/Documentation',
                'video_link': 'https://help.example.com/videos/export-data'
            },
            {
                'question': 'Invoice request',
                'answer': 'I\'ll be happy to help with your invoice request.\n\nPlease provide:\n- Company name\n- Invoice period/month\n- Billing email address\n\nOur billing team will send the invoice within 24 hours.',
                'category': 'Billing/Invoice',
                'manual_link': 'https://help.example.com/docs/billing-faq'
            }
        ]
    
    def generate_response(
        self,
        subject: str,
        body: str,
        sender_name: str,
        category: str,
        severity: str,
        ticket_id: str,
        sla_hours: int
    ) -> Dict:
        """
        Generate intelligent auto-response
        
        Returns:
            {
                'response_type': 'perfect_match' | 'partial_match' | 'acknowledgment',
                'response_text': str,
                'confidence': float,
                'auto_send': bool,
                'references': List[str],
                'similar_tickets': List[Dict]
            }
        """
        
        # 1. Search FAQ database
        faq_match = self._search_faq(subject, body, category)
        
        # 2. Search similar resolved tickets
        similar_tickets = self.embedding_service.search_similar(
            subject,
            body,
            top_k=3,
            threshold=0.80
        )
        
        # Filter for resolved tickets only
        resolved_tickets = [
            t for t in similar_tickets
            if t.get('resolution', '').strip()
        ]
        
        # 3. Determine response type and generate
        if faq_match and faq_match['similarity'] >= 0.90:
            # Perfect match - send complete solution
            return self._create_perfect_match_response(
                faq_match,
                sender_name,
                ticket_id,
                sla_hours,
                severity
            )
        
        elif faq_match and faq_match['similarity'] >= 0.60:
            # Partial match - suggest troubleshooting
            return self._create_partial_match_response(
                faq_match,
                resolved_tickets,
                sender_name,
                ticket_id,
                sla_hours,
                severity
            )
        
        elif resolved_tickets:
            # Use similar ticket resolutions
            return self._create_resolution_based_response(
                resolved_tickets,
                subject,
                body,
                sender_name,
                ticket_id,
                sla_hours,
                severity
            )
        
        else:
            # No match - send acknowledgment
            return self._create_acknowledgment_response(
                sender_name,
                category,
                ticket_id,
                sla_hours,
                severity
            )
    
    def _search_faq(self, subject: str, body: str, category: str) -> Optional[Dict]:
        """
        Search FAQ database for matching answers
        """
        query = f"{subject} {body}"
        
        best_match = None
        best_similarity = 0.0
        
        # Filter by category first
        category_faqs = [faq for faq in self.faq_database if faq['category'] == category]
        
        if not category_faqs:
            category_faqs = self.faq_database  # Fallback to all FAQs
        
        for faq in category_faqs:
            similarity = self.embedding_service.calculate_similarity(
                query,
                faq['question'] + " " + faq['answer']
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = faq.copy()
                best_match['similarity'] = similarity
        
        return best_match if best_match else None
    
    def _create_perfect_match_response(
        self,
        faq: Dict,
        sender_name: str,
        ticket_id: str,
        sla_hours: int,
        severity: str
    ) -> Dict:
        """
        Create response for perfect FAQ match
        """
        references = []
        if faq.get('video_link'):
            references.append(f"📹 Video Tutorial: {faq['video_link']}")
        if faq.get('manual_link'):
            references.append(f"📄 Documentation: {faq['manual_link']}")
        
        response_text = f"""Dear {sender_name},

Thank you for contacting IntelliDesk Support!

{faq['answer']}

"""
        
        if references:
            response_text += "**Additional Resources:**\n"
            response_text += "\n".join(references)
            response_text += "\n\n"
        
        if faq.get('success_rate'):
            response_text += f"📊 Success Rate: {faq['success_rate']}\n"
        
        if faq.get('avg_resolution_time'):
            response_text += f"⏱️ Average Resolution Time: {faq['avg_resolution_time']}\n\n"
        
        response_text += f"""If this doesn't resolve your issue, please reply to this email and our team will assist you further.

**Ticket ID:** {ticket_id}
**Priority:** {severity}

Best regards,
IntelliDesk AI Support"""
        
        # Auto-send if confidence high and severity low
        auto_send = faq['similarity'] >= AUTO_SEND_CONFIDENCE and severity in ['P3', 'P4']
        
        return {
            'response_type': 'perfect_match',
            'response_text': response_text,
            'confidence': faq['similarity'],
            'auto_send': auto_send,
            'references': references,
            'similar_tickets': []
        }
    
    def _create_partial_match_response(
        self,
        faq: Dict,
        resolved_tickets: List[Dict],
        sender_name: str,
        ticket_id: str,
        sla_hours: int,
        severity: str
    ) -> Dict:
        """
        Create response for partial match
        """
        response_text = f"""Dear {sender_name},

Thank you for contacting IntelliDesk Support!

Based on your inquiry, here are some suggestions that might help:

{faq['answer']}

"""
        
        if resolved_tickets:
            response_text += "\n**Similar Issues Resolved:**\n"
            for i, ticket in enumerate(resolved_tickets[:2], 1):
                response_text += f"{i}. {ticket['subject']} (Similarity: {ticket['similarity']*100:.0f}%)\n"
        
        response_text += f"""
Our support team has been notified and will respond within {sla_hours} hours.

**Ticket ID:** {ticket_id}
**Priority:** {severity}

Best regards,
IntelliDesk AI Support"""
        
        return {
            'response_type': 'partial_match',
            'response_text': response_text,
            'confidence': faq['similarity'],
            'auto_send': False,
            'references': [],
            'similar_tickets': resolved_tickets
        }
    
    def _create_resolution_based_response(
        self,
        resolved_tickets: List[Dict],
        subject: str,
        body: str,
        sender_name: str,
        ticket_id: str,
        sla_hours: int,
        severity: str
    ) -> Dict:
        """
        Create response based on similar resolved tickets
        """
        # Use AI to synthesize resolution
        prompt = f"""Based on these similar resolved support tickets, create a helpful response:

Current Issue:
Subject: {subject}
Description: {body[:300]}

Similar Resolved Tickets:
"""
        for i, ticket in enumerate(resolved_tickets[:2], 1):
            prompt += f"\n{i}. {ticket['subject']}\n   Resolution: {ticket.get('resolution', 'N/A')[:200]}\n"
        
        prompt += f"""
Create a brief, helpful response suggesting common solutions.
Keep it under 150 words and actionable."""
        
        try:
            response = self.model.generate_content(prompt)
            ai_suggestion = response.text.strip()
            
            response_text = f"""Dear {sender_name},

Thank you for contacting IntelliDesk Support!

{ai_suggestion}

Based on {len(resolved_tickets)} similar cases, common solutions included the steps above.

Our support team will review your specific case and respond within {sla_hours} hours.

**Ticket ID:** {ticket_id}
**Priority:** {severity}

Best regards,
IntelliDesk AI Support"""
            
            return {
                'response_type': 'resolution_based',
                'response_text': response_text,
                'confidence': resolved_tickets[0]['similarity'],
                'auto_send': False,
                'references': [],
                'similar_tickets': resolved_tickets
            }
            
        except Exception as e:
            # Fallback to acknowledgment
            return self._create_acknowledgment_response(
                sender_name,
                '',
                ticket_id,
                sla_hours,
                severity
            )
    
    def _create_acknowledgment_response(
        self,
        sender_name: str,
        category: str,
        ticket_id: str,
        sla_hours: int,
        severity: str
    ) -> Dict:
        """
        Create acknowledgment response (no match)
        """
        response_text = f"""Dear {sender_name},

Thank you for contacting IntelliDesk Support!

We have received your inquiry and assigned it to our team for review.

A support specialist will respond within {sla_hours} hours with a solution or next steps.

**Ticket ID:** {ticket_id}
**Priority:** {severity}
**Estimated Response Time:** {sla_hours} hours

To help us serve you better, please include any error messages, screenshots, or additional details if you haven't already.

Best regards,
IntelliDesk AI Support"""
        
        return {
            'response_type': 'acknowledgment',
            'response_text': response_text,
            'confidence': 0.0,
            'auto_send': True,  # Always auto-send acknowledgments
            'references': [],
            'similar_tickets': []
        }


    def generate_perfect_reply(
        self,
        subject: str,
        body: str,
        sender_email: str,
        category: str,
        severity: str,
        confidence: float
    ) -> Dict:
        """
        Generate a perfect, context-aware resolution email using Gemini LLM
        This is used for manual resolution with pre-filled high-quality responses
        
        Returns:
            {
                'reply_text': str,
                'should_auto_send': bool (True if confidence > 90%)
            }
        """
        # Extract sender name and company from email
        sender_name = sender_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        company_name = sender_email.split('@')[1].split('.')[0].title() if '@' in sender_email else 'Valued Customer'
        
        # Create comprehensive prompt for LLM
        prompt = f"""You are a professional customer support specialist. Generate a perfect resolution email for this support ticket.

Ticket Details:
- Subject: {subject}
- Category: {category}
- Severity: {severity}
- Customer Email: {sender_email}
- Customer Name: {sender_name}
- Company: {company_name}
- Classification Confidence: {confidence*100:.1f}%

Customer's Issue:
{body[:500]}

Instructions:
1. Address the customer by name warmly
2. Show empathy and understanding
3. Provide a clear, actionable solution
4. Include step-by-step instructions if applicable
5. Offer additional help if needed
6. Keep professional but friendly tone
7. Sign off professionally
8. Keep response under 250 words

Generate the complete email response:"""
        
        try:
            response = self.model.generate_content(prompt)
            reply_text = response.text.strip()
            
            # Clean up any markdown formatting
            reply_text = reply_text.replace('**', '').replace('*', '')
            
            # Determine if should auto-send (confidence > 90%)
            should_auto_send = confidence > 0.90
            
            return {
                'reply_text': reply_text,
                'should_auto_send': should_auto_send,
                'sender_name': sender_name,
                'company_name': company_name
            }
            
        except Exception as e:
            print(f"Error generating perfect reply: {e}")
            # Fallback template
            fallback_text = f"""Dear {sender_name},

Thank you for contacting {company_name} Support!

We have carefully reviewed your inquiry regarding: {subject}

Our team is working on a resolution and will provide you with a detailed solution shortly. In the meantime, if you have any additional information that might help us resolve this faster, please feel free to reply to this email.

We appreciate your patience and are committed to resolving your issue as quickly as possible.

Best regards,
IntelliDesk Support Team

Ticket Category: {category}
Priority: {severity}"""
            
            return {
                'reply_text': fallback_text,
                'should_auto_send': False,
                'sender_name': sender_name,
                'company_name': company_name
            }


# Singleton instance
auto_response_service = AutoResponseService()
