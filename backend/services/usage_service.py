import sqlite3
import uuid
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')


def track_usage(user_id: str, words: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_tracking (id, user_id, words_processed, requests_count)
        VALUES (?, ?, ?, 1)
    """, (
        str(uuid.uuid4()),
        user_id,
        words
    ))

    conn.commit()
    conn.close()


def get_daily_usage(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(requests_count)
        FROM usage_tracking
        WHERE user_id=?
        AND date(created_at)=date('now')
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result[0] else 0
