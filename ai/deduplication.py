"""
Thread Detection & Deduplication Module
Detects email threads and prevents duplicate tickets
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from .embeddings import embedding_service
from .ai_config import (
    SIMILARITY_THRESHOLD,
    THREAD_WINDOW_HOURS,
    SAME_SENDER_WINDOW_HOURS
)


class DeduplicationService:
    """
    Handles email thread detection and deduplication
    """
    
    def __init__(self):
        self.embedding_service = embedding_service
    
    def detect_thread(
        self,
        email_headers: Dict,
        subject: str,
        body: str,
        sender: str,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Detect if email is part of existing thread
        
        Args:
            email_headers: Email headers (In-Reply-To, References, Message-ID)
            subject: Email subject
            body: Email body
            sender: Sender email
            existing_tickets: List of existing tickets to check against
            
        Returns:
            Existing ticket dict if match found, None otherwise
        """
        
        # 1. Check header-based threading
        header_match = self._check_header_threading(email_headers, existing_tickets)
        if header_match:
            return header_match
        
        # 2. Check subject line patterns (Re:, Fwd:, ticket references)
        subject_match = self._check_subject_patterns(subject, existing_tickets)
        if subject_match:
            return subject_match
        
        # 3. Check ticket reference parsing
        ticket_ref_match = self._check_ticket_references(subject, body, existing_tickets)
        if ticket_ref_match:
            return ticket_ref_match
        
        # 4. Check same sender within time window
        sender_match = self._check_same_sender(sender, subject, existing_tickets)
        if sender_match:
            return sender_match
        
        # 5. Semantic similarity check
        semantic_match = self._check_semantic_similarity(subject, body, existing_tickets)
        if semantic_match:
            return semantic_match
        
        return None
    
    def _check_header_threading(
        self,
        headers: Dict,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Check email headers for thread relationship
        """
        in_reply_to = headers.get('In-Reply-To', '')
        references = headers.get('References', '')
        
        if not in_reply_to and not references:
            return None
        
        # Extract Message-IDs from References header
        ref_ids = re.findall(r'<([^>]+)>', references)
        if in_reply_to:
            ref_ids.append(in_reply_to.strip('<>'))
        
        # Check if any existing ticket has matching Message-ID
        for ticket in existing_tickets:
            ticket_msg_id = ticket.get('message_id', '')
            if ticket_msg_id in ref_ids:
                return ticket
        
        return None
    
    def _check_subject_patterns(
        self,
        subject: str,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Check subject line patterns (Re:, Fwd:, etc.)
        """
        # Normalize subject (remove Re:, Fwd:, etc.)
        normalized_subject = self._normalize_subject(subject)
        
        # Check against existing tickets
        for ticket in existing_tickets:
            ticket_subject = ticket.get('subject', '')
            normalized_ticket_subject = self._normalize_subject(ticket_subject)
            
            # Fuzzy match
            if self._fuzzy_match(normalized_subject, normalized_ticket_subject):
                # Check time window
                if self._within_time_window(ticket, THREAD_WINDOW_HOURS):
                    return ticket
        
        return None
    
    def _check_ticket_references(
        self,
        subject: str,
        body: str,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Parse ticket references from subject/body
        Examples: #12345, Ticket-12345, INC000123
        """
        text = subject + " " + body
        
        # Extract ticket references
        patterns = [
            r'#(\d{4,})',
            r'Ticket[:\s#-]*(\d{4,})',
            r'INC(\d{6,})',
            r'TICKET[:\s#-]*(\d{4,})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Look for ticket with this ID
                for ticket in existing_tickets:
                    ticket_id = str(ticket.get('ticket_id', ''))
                    if match in ticket_id:
                        return ticket
        
        return None
    
    def _check_same_sender(
        self,
        sender: str,
        subject: str,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Check for same sender within time window
        """
        normalized_subject = self._normalize_subject(subject)
        
        for ticket in existing_tickets:
            ticket_sender = ticket.get('sender', '')
            ticket_subject = ticket.get('subject', '')
            
            if sender.lower() == ticket_sender.lower():
                # Same sender - check subject similarity
                if self._fuzzy_match(normalized_subject, self._normalize_subject(ticket_subject)):
                    # Check within 48-hour window
                    if self._within_time_window(ticket, SAME_SENDER_WINDOW_HOURS):
                        return ticket
        
        return None
    
    def _check_semantic_similarity(
        self,
        subject: str,
        body: str,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Check semantic similarity using embeddings
        """
        # Only check recent tickets (within 72 hours)
        recent_tickets = [
            t for t in existing_tickets
            if self._within_time_window(t, THREAD_WINDOW_HOURS)
        ]
        
        if not recent_tickets:
            return None
        
        # Search for similar tickets
        similar_tickets = self.embedding_service.search_similar(
            subject,
            body,
            top_k=3,
            threshold=SIMILARITY_THRESHOLD
        )
        
        if similar_tickets:
            # Return most similar
            return similar_tickets[0]
        
        return None
    
    def _normalize_subject(self, subject: str) -> str:
        """
        Normalize subject line for comparison
        Remove Re:, Fwd:, timestamps, etc.
        """
        normalized = subject.lower()
        
        # Remove common prefixes
        prefixes = [r're:', r'fwd:', r'fw:', r'response:', r'answer:']
        for prefix in prefixes:
            normalized = re.sub(f'^{prefix}\\s*', '', normalized)
        
        # Remove ticket references
        normalized = re.sub(r'\[ticket\\s*#?\\d+\]', '', normalized, flags=re.IGNORECASE)
        
        # Remove timestamps
        normalized = re.sub(r'\d{1,2}:\d{2}', '', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def _fuzzy_match(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """
        Fuzzy string matching
        """
        # Simple character-based similarity
        if not text1 or not text2:
            return False
        
        # Exact match
        if text1 == text2:
            return True
        
        # Calculate Jaccard similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return False
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def _within_time_window(self, ticket: Dict, hours: int) -> bool:
        """
        Check if ticket is within time window
        """
        ticket_time = ticket.get('created_at')
        
        if isinstance(ticket_time, str):
            ticket_time = datetime.fromisoformat(ticket_time.replace('Z', '+00:00'))
        
        if not ticket_time:
            return False
        
        time_diff = datetime.utcnow() - ticket_time.replace(tzinfo=None)
        return time_diff.total_seconds() / 3600 <= hours
    
    def is_duplicate(
        self,
        subject: str,
        body: str,
        sender: str,
        existing_tickets: List[Dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if email is a duplicate
        
        Returns:
            (is_duplicate, master_ticket_id)
        """
        match = self.detect_thread(
            {},  # No headers available
            subject,
            body,
            sender,
            existing_tickets
        )
        
        if match:
            return True, match.get('ticket_id')
        
        return False, None


# Singleton instance
deduplication_service = DeduplicationService()
