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
        Examples: #12345, Ticket-12345, INC000123, [Ticket #12345]
        """
        text = subject + " " + body
        
        # Comprehensive ticket reference patterns
        patterns = [
            r'#(\d{4,})',                           # #12345
            r'Ticket[:\s#-]+(\d{4,})',             # Ticket-12345, Ticket: 12345, Ticket #12345
            r'INC(\d{6,})',                         # INC000123
            r'TICKET[:\s#-]+(\d{4,})',             # TICKET-12345
            r'\[Ticket\s*#?(\d{4,})\]',            # [Ticket #12345]
            r'REQ(\d{6,})',                         # REQ000123
            r'case[:\s#-]+(\d{4,})',               # case-12345
            r'ref[:\s#-]+(\d{4,})',                # ref-12345
            r'ID[:\s#-]+(\d{4,})',                 # ID-12345
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Look for ticket with this ID
                for ticket in existing_tickets:
                    ticket_id = str(ticket.get('ticket_id', ''))
                    # Match against ticket number (numeric part)
                    if match in ticket_id or ticket_id.endswith(match):
                        return ticket
        
        return None
    
    def _check_same_sender(
        self,
        sender: str,
        subject: str,
        existing_tickets: List[Dict]
    ) -> Optional[Dict]:
        """
        Check for same sender on same topic within 48-hour window
        Groups emails from same sender within 48 hours
        """
        normalized_subject = self._normalize_subject(subject)
        
        for ticket in existing_tickets:
            ticket_sender = ticket.get('sender', '')
            ticket_subject = ticket.get('subject', '')
            
            if sender.lower() == ticket_sender.lower():
                # Same sender - check subject similarity
                if self._fuzzy_match(normalized_subject, self._normalize_subject(ticket_subject)):
                    # Check within 48-hour window (as specified)
                    if self._within_time_window(ticket, 48):
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
        Uses 85% threshold within 72-hour window
        """
        # Only check recent tickets (within 72 hours)
        recent_tickets = [
            t for t in existing_tickets
            if self._within_time_window(t, 72)  # 72 hours as specified
        ]
        
        if not recent_tickets:
            return None
        
        # Search for similar tickets with 85% threshold
        similar_tickets = self.embedding_service.search_similar(
            subject,
            body,
            top_k=5,
            threshold=0.85  # 85% similarity as specified
        )
        
        if similar_tickets:
            # Return most similar
            return similar_tickets[0]
        
        return None
    
    def _normalize_subject(self, subject: str) -> str:
        """
        Normalize subject line for comparison
        Remove Re:, Fwd:, timestamps, ticket references, etc.
        """
        normalized = subject.lower()
        
        # Remove common prefixes (including multilingual)
        prefixes = [
            r're:', r'fwd:', r'fw:', r'response:', r'answer:', 
            r'réf:', r'rép:', r'res:', r'rv:', r'vs:', r'aw:',
            r'antw:', r'sv:', r'ref:', r'ynt:', r'wg:'
        ]
        for prefix in prefixes:
            # Remove prefix multiple times (Re: Re: Re:)
            while re.search(f'^{prefix}\\s*', normalized):
                normalized = re.sub(f'^{prefix}\\s*', '', normalized)
        
        # Remove ticket references and brackets
        normalized = re.sub(r'\[ticket\s*#?\d+\]', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\[#?\d+\]', '', normalized)
        normalized = re.sub(r'ticket[:\s#-]+\d+', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'#\d+', '', normalized)
        normalized = re.sub(r'INC\d+', '', normalized, flags=re.IGNORECASE)
        
        # Remove timestamps (various formats)
        normalized = re.sub(r'\d{1,2}:\d{2}(:\d{2})?(\s*[ap]m)?', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', normalized)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}', '', normalized)
        
        # Remove common email artifacts
        normalized = re.sub(r'\s*-\s*$', '', normalized)  # Trailing dashes
        normalized = re.sub(r'^\s*-\s*', '', normalized)  # Leading dashes
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def _fuzzy_match(self, text1: str, text2: str, threshold: float = 0.75) -> bool:
        """
        Fuzzy string matching using multiple algorithms
        """
        if not text1 or not text2:
            return False
        
        # Exact match
        if text1 == text2:
            return True
        
        # Calculate multiple similarity metrics
        
        # 1. Jaccard similarity (word-based)
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if words1 or words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            jaccard = len(intersection) / len(union) if union else 0
        else:
            jaccard = 0
        
        # 2. Character-based similarity (for typos)
        set1 = set(text1.replace(' ', ''))
        set2 = set(text2.replace(' ', ''))
        if set1 or set2:
            char_intersection = set1.intersection(set2)
            char_union = set1.union(set2)
            char_sim = len(char_intersection) / len(char_union) if char_union else 0
        else:
            char_sim = 0
        
        # 3. Substring containment
        shorter = text1 if len(text1) < len(text2) else text2
        longer = text2 if len(text1) < len(text2) else text1
        containment = 1.0 if shorter in longer and len(shorter) > 5 else 0
        
        # Combined score (weighted average)
        combined_score = (jaccard * 0.6) + (char_sim * 0.3) + (containment * 0.1)
        
        return combined_score >= threshold
    
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
