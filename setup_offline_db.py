"""
Setup database for standalone offline version
Creates test user: teacher / teacher123
FIXED: Uses correct schema with first_name, last_name, email
"""
import sqlite3
import hashlib
import os

# Database path for standalone version
DB_PATH = r"dist\ExamSystem\data\users.db"

def setup_database():
    """Create database with correct schema and test user"""
    # Delete old database if exists (to fix schema)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️  Removed old database")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect and create table with CORRECT schema
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    cursor = conn.cursor()
    
    # Create users table with full schema (matching auth_service.py)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            terms_accepted_at TIMESTAMP
        )
    ''')
    
    # Create test user with first_name and last_name
    password_hash = hashlib.sha256('teacher123'.encode()).hexdigest()
    cursor.execute('''
        INSERT INTO users (username, password_hash, first_name, last_name, email, terms_accepted_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', ('teacher', password_hash, 'Test', 'Teacher', 'teacher@example.com'))
    
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print("📁 Location:", os.path.abspath(DB_PATH))
    print("👤 Test user: teacher")
    print("🔑 Password:  teacher123")
    print("📧 Name: Test Teacher")
    print("📧 Email: teacher@example.com")

if __name__ == "__main__":
    setup_database()
