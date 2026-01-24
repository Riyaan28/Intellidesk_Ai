"""
Re-classify all existing tickets with new urgency detection logic
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models import Ticket
from ai.urgency import urgency_detector

def reclassify_all_tickets():
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        
        print(f"Re-classifying {len(tickets)} tickets...\n")
        
        for ticket in tickets:
            # Re-run urgency detection with new logic
            urgency = urgency_detector.detect_urgency(
                subject=ticket.subject,
                body=ticket.body,
                category=ticket.category,
                followup_count=ticket.followup_count or 0
            )
            
            # Update ticket with new severity
            old_severity = ticket.severity
            ticket.severity = urgency['severity']
            ticket.severity_name = urgency['severity_name']
            ticket.sla_hours = urgency['sla_hours']
            ticket.sla_deadline = urgency['sla_deadline']
            ticket.urgency_signals = urgency.get('signals', [])
            ticket.urgency_reasoning = urgency.get('reasoning', '')
            
            print(f"✅ {ticket.ticket_id}: {old_severity} → {urgency['severity']} ({urgency['severity_name']})")
            print(f"   Reasoning: {urgency['reasoning']}")
            print(f"   Signals: {len(urgency.get('signals', []))} detected\n")
        
        db.commit()
        
        # Show distribution
        print("\n" + "="*60)
        print("NEW SEVERITY DISTRIBUTION:")
        print("="*60)
        from sqlalchemy import func
        severity_counts = db.query(
            Ticket.severity, 
            func.count(Ticket.id)
        ).group_by(Ticket.severity).all()
        
        for severity, count in severity_counts:
            print(f"{severity}: {count} tickets")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reclassify_all_tickets()
