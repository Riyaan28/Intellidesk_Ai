"""
Test Ticket Generator
Generates random tickets for testing purposes
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict


class TestTicketGenerator:
    """Generate random tickets for testing"""
    
    CATEGORIES = [
        "Technical Support",
        "Access Request", 
        "Billing/Invoice",
        "Feature Request",
        "Hardware Issue",
        "How-To/Documentation",
        "Data Request",
        "Bug Report",
        "General Inquiry"
    ]
    
    SEVERITIES = ["P1", "P2", "P3", "P4"]
    
    SAMPLE_ISSUES = [
        {
            "subject": "Cannot login to my account",
            "body": "Hi, I've been trying to log in for the past hour but keep getting an error message saying 'Invalid credentials'. I've reset my password twice already. Please help urgently!",
            "category": "Access Request",
            "severity": "P1"
        },
        {
            "subject": "Payment not reflecting in account", 
            "body": "Hello, I made a payment of $299 on January 20th but it's still not showing in my account. Transaction ID: TXN-45678. Could you please check?",
            "category": "Billing/Invoice",
            "severity": "P2"
        },
        {
            "subject": "Feature request: Dark mode",
            "body": "Would love to see a dark mode option in the app. Many users including myself work late hours and bright screens cause eye strain.",
            "category": "Feature Request",
            "severity": "P4"
        },
        {
            "subject": "Application crashing on startup",
            "body": "URGENT: The app crashes immediately after launching. I'm on Windows 11, version 2.5.1. Error code: 0xc0000005. This is blocking my work!",
            "category": "Technical Support",
            "severity": "P1"
        },
        {
            "subject": "How do I export my data?",
            "body": "Hi team, I need to export all my data to Excel format for a presentation. Can you guide me through the steps? Thanks!",
            "category": "How-To/Documentation",
            "severity": "P3"
        },
        {
            "subject": "Printer not working with new update",
            "body": "After the latest software update, my HP LaserJet printer is no longer recognized. I've tried reinstalling drivers but no luck. Need help ASAP.",
            "category": "Hardware Issue",
            "severity": "P2"
        },
        {
            "subject": "Need GDPR data deletion request",
            "body": "As per GDPR regulations, I request complete deletion of my personal data from your systems. Please confirm once done.",
            "category": "Data Request",
            "severity": "P2"
        },
        {
            "subject": "Dashboard shows incorrect metrics",
            "body": "The dashboard is displaying wrong numbers for total sales. It shows $12,000 but our actual sales are $18,500. This is affecting our reports.",
            "category": "Bug Report",
            "severity": "P2"
        },
        {
            "subject": "Question about enterprise plan",
            "body": "Hi, I'm interested in upgrading to the enterprise plan. Can you provide more details about the features and pricing?",
            "category": "General Inquiry",
            "severity": "P3"
        },
        {
            "subject": "API returning 500 errors",
            "body": "CRITICAL: Our production API has been returning 500 errors for the past 15 minutes. This is affecting thousands of users. Endpoint: /api/v2/users. Please investigate immediately!",
            "category": "Technical Support",
            "severity": "P1"
        }
    ]
    
    SENDERS = [
        "john.smith@acme.com",
        "sarah.johnson@techcorp.io",
        "mike.wilson@startup.co",
        "emily.brown@enterprise.net",
        "david.lee@innovate.com",
        "lisa.martinez@global.org",
        "james.anderson@company.com"
    ]
    
    def generate_random_tickets(self, count: int = 7) -> List[Dict]:
        """
        Generate random test tickets
        
        Args:
            count: Number of tickets to generate
            
        Returns:
            List of ticket dictionaries
        """
        tickets = []
        
        # Shuffle sample issues and senders
        issues = random.sample(self.SAMPLE_ISSUES, min(count, len(self.SAMPLE_ISSUES)))
        
        # If we need more tickets than samples, repeat with variations
        while len(issues) < count:
            base_issue = random.choice(self.SAMPLE_ISSUES)
            variation = base_issue.copy()
            variation['subject'] = f"Re: {variation['subject']}"
            issues.append(variation)
        
        for i, issue in enumerate(issues[:count]):
            sender = random.choice(self.SENDERS)
            
            # Add some time variation
            hours_ago = random.randint(1, 48)
            created_at = datetime.utcnow() - timedelta(hours=hours_ago)
            
            ticket = {
                "subject": issue["subject"],
                "body": issue["body"],
                "sender": sender,
                "category": issue["category"],
                "severity": issue["severity"],
                "created_at": created_at
            }
            
            tickets.append(ticket)
        
        return tickets


# Singleton instance
test_ticket_generator = TestTicketGenerator()
