"""
Database Migration: Create Knowledge Base Table
Run this to create the knowledge_base table
"""

from sqlalchemy import create_engine, text, inspect
from database import DATABASE_URL
import sys

def table_exists(engine, table_name):
    """Check if table already exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate():
    """Create knowledge_base table"""
    engine = create_engine(DATABASE_URL)
    
    create_table_sql = """
    CREATE TABLE knowledge_base (
        id INTEGER PRIMARY KEY,
        problem_summary TEXT NOT NULL,
        resolution_steps TEXT NOT NULL,
        category VARCHAR(100) NOT NULL,
        source_ticket_id INTEGER NOT NULL UNIQUE,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        usage_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_ticket_id) REFERENCES tickets(id)
    )
    """
    
    create_index_sql = "CREATE INDEX ix_knowledge_base_category ON knowledge_base(category)"
    create_id_index_sql = "CREATE INDEX ix_knowledge_base_id ON knowledge_base(id)"
    
    try:
        if table_exists(engine, 'knowledge_base'):
            print("⏭️  Table 'knowledge_base' already exists, skipping migration...")
            return
        
        with engine.connect() as conn:
            print("Creating knowledge_base table...")
            conn.execute(text(create_table_sql))
            conn.commit()
            
            print("Creating indexes...")
            conn.execute(text(create_index_sql))
            conn.execute(text(create_id_index_sql))
            conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("Knowledge Base table created with:")
        print("  - id (INTEGER PRIMARY KEY)")
        print("  - problem_summary (TEXT)")
        print("  - resolution_steps (TEXT)")
        print("  - category (VARCHAR(100), INDEXED)")
        print("  - source_ticket_id (INTEGER, UNIQUE, FK to tickets)")
        print("  - is_active (BOOLEAN, DEFAULT TRUE)")
        print("  - usage_count (INTEGER, DEFAULT 0)")
        print("  - created_at (TIMESTAMP)")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure no other process is using the database")
        print("2. Check if the database file exists and is writable")
        print("3. Try stopping the backend server and running migration again")
        sys.exit(1)

if __name__ == "__main__":
    print("Running migration to create Knowledge Base table...")
    migrate()
