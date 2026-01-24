"""
Initialize Database
Run this script to create all tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, engine
from models import Customer, User, Ticket, EmailLog, Analytics

def init_db():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("Tables created:")
        print("  - customers")
        print("  - users")
        print("  - tickets")
        print("  - email_logs")
        print("  - analytics")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise

if __name__ == "__main__":
    init_db()
