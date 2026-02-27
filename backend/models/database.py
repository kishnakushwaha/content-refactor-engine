import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        subscription_tier TEXT DEFAULT 'free',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # USAGE TRACKING TABLE (CRITICAL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_tracking (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        words_processed INTEGER DEFAULT 0,
        requests_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ARTICLES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        original_content TEXT,
        rewritten_content TEXT,
        similarity_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Insert a dummy admin user for MVP testing
    cursor.execute("SELECT id FROM users WHERE email='admin@cre.com'")
    if not cursor.fetchone():
        admin_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (id, email, api_key, subscription_tier) VALUES (?, ?, ?, ?)",
            (admin_id, 'admin@cre.com', 'cre-admin-key-12345', 'enterprise')
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
