import sqlite3
import os

DB_PATH = 'backend/monitoring.db'

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(bookmarks)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'category' not in columns:
            print("Adding 'category' column to 'bookmarks' table...")
            # Default to 'post' as requested
            cursor.execute("ALTER TABLE bookmarks ADD COLUMN category VARCHAR(50) DEFAULT 'post'")
            conn.commit()
            print("Migration successful.")
        else:
            print("'category' column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
