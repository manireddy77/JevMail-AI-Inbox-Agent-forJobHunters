import sqlite3
import os
import json
from app.config import DATABASE_PATH
from app.utils.logging import logger


def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            gmail_message_id    TEXT PRIMARY KEY,
            thread_id           TEXT,
            sender              TEXT,
            subject             TEXT,
            received_at         TEXT,
            body_snippet        TEXT,
            processed_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            probabilities       TEXT,
            category            TEXT,
            action_taken        TEXT,
            insight             TEXT,
            model               TEXT,
            provider            TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_count INTEGER,
            mode            TEXT
        )
    """)
    conn.commit()
    # Migrate: add new columns to existing tables if needed
    _migrate(conn)
    conn.close()


def _migrate(conn):
    """Add columns that may not exist in older versions of the schema."""
    cursor = conn.cursor()
    existing = {row[1] for row in cursor.execute("PRAGMA table_info(emails)")}
    new_cols = {
        "body_snippet": "TEXT",
        "category":     "TEXT",
        "insight":      "TEXT",
    }
    for col, col_type in new_cols.items():
        if col not in existing:
            try:
                cursor.execute(f"ALTER TABLE emails ADD COLUMN {col} {col_type}")
                conn.commit()
            except Exception as e:
                logger.debug(f"Migration skipped for {col}: {e}")


def is_processed(gmail_message_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM emails WHERE gmail_message_id = ?", (gmail_message_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def save_email_processing(
    message_id: str,
    thread_id: str,
    sender: str,
    subject: str,
    received_at: str,
    body_snippet: str,
    probabilities: dict,
    category: str,
    action_taken: str,
    insight: str,
    model: str,
    provider: str
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO emails
        (gmail_message_id, thread_id, sender, subject, received_at,
         body_snippet, probabilities, category, action_taken, insight, model, provider)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message_id, thread_id, sender, subject, received_at,
        body_snippet[:500],
        json.dumps(probabilities),
        category,
        action_taken,
        insight,
        model,
        provider
    ))
    conn.commit()
    conn.close()


def get_all_emails(limit=200):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM emails ORDER BY processed_at DESC LIMIT ?", (limit,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    for r in rows:
        try:
            r["probabilities"] = json.loads(r.get("probabilities") or "{}")
        except Exception:
            r["probabilities"] = {}
    return rows


def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM emails GROUP BY category")
    rows = cursor.fetchall()
    conn.close()
    return {row["category"] or "UNKNOWN": row["count"] for row in rows}
