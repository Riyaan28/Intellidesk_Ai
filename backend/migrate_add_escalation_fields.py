"""
Database Migration: Add Follow-up and Escalation Fields
Run this to add new columns to existing tickets table
"""

from sqlalchemy import create_engine, text, inspect
from database import DATABASE_URL
import sys

def column_exists(engine, table_name, column_name):
    """Check if column already exists"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate():
    """Add new escalation tracking columns"""
    engine = create_engine(DATABASE_URL)
    
    migrations = [
        ('followup_count', 'ALTER TABLE tickets ADD COLUMN followup_count INTEGER DEFAULT 0'),
        ('is_escalated', 'ALTER TABLE tickets ADD COLUMN is_escalated BOOLEAN DEFAULT 0'),
        ('escalation_reason', 'ALTER TABLE tickets ADD COLUMN escalation_reason VARCHAR(255)'),
        ('escalation_time', 'ALTER TABLE tickets ADD COLUMN escalation_time TIMESTAMP')
    ]
    
    try:
        with engine.connect() as conn:
            for column_name, migration_sql in migrations:
                if column_exists(engine, 'tickets', column_name):
                    print(f"⏭️  Column '{column_name}' already exists, skipping...")
                    continue
                
                print(f"Adding column '{column_name}'...")
                conn.execute(text(migration_sql))
                conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("Database is now up to date with escalation tracking fields:")
        print("  - followup_count (INTEGER)")
        print("  - is_escalated (BOOLEAN)")
        print("  - escalation_reason (VARCHAR)")
        print("  - escalation_time (TIMESTAMP)")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure no other process is using the database")
        print("2. Check if the database file exists and is writable")
        print("3. Try stopping the backend server and running migration again")
        sys.exit(1)

if __name__ == "__main__":
    print("Running migration to add escalation tracking fields...")
    migrate()
