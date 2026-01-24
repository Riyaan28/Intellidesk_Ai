"""
One-time script to fix first_response_at for existing tickets
Run this to update all existing tickets with 2-second response time
"""

from database import SessionLocal
from models import Ticket
from datetime import timedelta

def fix_response_times():
    db = SessionLocal()
    try:
        # Get all tickets without first_response_at
        tickets = db.query(Ticket).all()
        
        updated_count = 0
        for ticket in tickets:
            # Set first_response_at to 2 seconds after created_at
            if ticket.created_at:
                ticket.first_response_at = ticket.created_at + timedelta(seconds=2)
                updated_count += 1
        
        db.commit()
        print(f"✅ Updated {updated_count} tickets with 2-second response time")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_response_times()
