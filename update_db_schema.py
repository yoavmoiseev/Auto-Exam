"""
Update database schema to add terms_accepted_at column to existing users table
Run this script once to migrate existing database
"""

import sqlite3
import os
from config import app_config

def update_schema():
    """Add terms_accepted_at column if it doesn't exist"""
    db_path = app_config.DATABASE_PATH
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. It will be created with the new schema.")
        return
    
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'terms_accepted_at' not in columns:
            print("Adding 'terms_accepted_at' column to users table...")
            cursor.execute('''
                ALTER TABLE users ADD COLUMN terms_accepted_at TIMESTAMP
            ''')
            conn.commit()
            print("✓ Column 'terms_accepted_at' added successfully!")
        else:
            print("✓ Column 'terms_accepted_at' already exists. No changes needed.")
        
        # Display current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nCurrent users table schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Database Schema Update Tool")
    print("=" * 50)
    update_schema()
    print("=" * 50)
    print("Done!")
