"""
Contact Information Extractor
Extracts name, phone, email, address, company from email body and signature
"""

import re
from typing import Dict, Optional, List


class ContactExtractor:
    """
    Extract contact information from email body using regex patterns
    """
    
    def __init__(self):
        # Phone patterns (US, India, International)
        self.phone_patterns = [
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # US: +1-555-123-4567
            r'\+91[-.\s]?(\d{10})',  # India: +91-9876543210
            r'\+\d{1,3}[-.\s]?\d{6,14}',  # International
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # 555-123-4567
            r'\b\d{10}\b'  # 9876543210
        ]
        
        # Email pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Company indicators
        self.company_keywords = [
            'Corp', 'Inc', 'LLC', 'Ltd', 'Limited', 'Corporation',
            'Company', 'Pvt', 'Private', 'Solutions', 'Technologies',
            'Tech', 'Systems', 'Services', 'Enterprises', 'Group'
        ]
        
        # Address patterns (simplified)
        self.address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)',
            r'(?:Suite|Ste|Unit|Apt|Apartment)\s*#?\d+',
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\s*\d{5}',  # City, ST 12345
        ]
    
    def extract_all(self, email_body: str, sender_email: str) -> Dict:
        """
        Extract all contact information from email
        
        Returns:
            {
                'name': str,
                'email': str,
                'phone': str,
                'company': str,
                'address': str,
                'title': str
            }
        """
        return {
            'name': self.extract_name(email_body, sender_email),
            'email': sender_email or self.extract_email(email_body),
            'phone': self.extract_phone(email_body),
            'company': self.extract_company(email_body, sender_email),
            'address': self.extract_address(email_body),
            'title': self.extract_title(email_body)
        }
    
    def extract_name(self, text: str, sender_email: str = "") -> Optional[str]:
        """
        Extract person name from email signature or salutation
        PRIMARY: Parse from email (before @) - john.doe@company.com -> John Doe
        FALLBACK: Parse from signature in email body
        """
        # PRIMARY: Extract from email address (before @)
        if sender_email and '@' in sender_email:
            username = sender_email.split('@')[0]
            # Convert john.doe or john_doe to John Doe
            name = username.replace('.', ' ').replace('_', ' ').replace('-', ' ')
            return ' '.join(word.capitalize() for word in name.split())
        
        # FALLBACK: Try signature patterns in email body
        signature_patterns = [
            r'(?:Best regards|Regards|Thanks|Sincerely|Cheers),?\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?:^|\n)\s*([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n\s*(?:[A-Z][a-z]+\s+(?:Manager|Director|Engineer|Lead|Head|VP|CEO|CTO))',
            r'From:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """
        Extract phone number from text
        """
        for pattern in self.phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        return None
    
    def extract_email(self, text: str) -> Optional[str]:
        """
        Extract email address from text
        """
        match = re.search(self.email_pattern, text)
        return match.group(0) if match else None
    
    def extract_company(self, text: str, sender_email: str = "") -> Optional[str]:
        """
        Extract company name from signature or email domain
        PRIMARY: Parse from email domain (after @) - john@acme.com -> Acme
        FALLBACK: Parse from signature/body
        """
        # PRIMARY: Extract from email domain (after @)
        if sender_email and '@' in sender_email:
            domain = sender_email.split('@')[1]
            # Get company name (before first dot)
            company = domain.split('.')[0]
            # Capitalize properly
            return company.title()
        
        # FALLBACK: Try to find in signature
        # Look for lines with company keywords
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Check if line contains company keywords
            for keyword in self.company_keywords:
                if keyword in line:
                    # Return the line or nearby lines
                    if len(line) > 5 and len(line) < 60:
                        return line
        
        # Try to find company from email domain
        email_match = re.search(self.email_pattern, text)
        if email_match:
            email = email_match.group(0)
            domain = email.split('@')[1] if '@' in email else ''
            if domain and not domain.startswith(('gmail', 'yahoo', 'hotmail', 'outlook')):
                # Extract company name from domain
                company = domain.split('.')[0]
                return company.capitalize() + ' Inc.'
        
        return None
    
    def extract_address(self, text: str) -> Optional[str]:
        """
        Extract address from email body
        """
        addresses = []
        
        for pattern in self.address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            addresses.extend(matches)
        
        if addresses:
            return ', '.join(addresses[:2])  # Return first 2 address components
        
        return None
    
    def extract_title(self, text: str) -> Optional[str]:
        """
        Extract job title from signature
        """
        title_patterns = [
            r'\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Manager|Director|Engineer|Lead|Developer|Designer|Analyst|Specialist|Coordinator|VP|CEO|CTO|CFO|COO))\s*\n',
            r'\n\s*((?:Senior|Junior|Lead|Chief|Principal|Staff)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None


# Singleton instance
contact_extractor = ContactExtractor()
