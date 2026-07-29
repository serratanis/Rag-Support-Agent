import sqlite3
from datetime import datetime, timedelta

from config import CONVERSATION_TIMEOUT_MINUTES

DB_PATH = "conversations.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,       -- 'user' or 'assistant'
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    return conn


def save_message(session_id: str, role: str, content: str):
    conn = _get_connection()
    with conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.utcnow().isoformat())
        )
    conn.close()


def get_recent_history(session_id: str, limit: int = 6):
    """Returns up to `limit` messages from the last conversation (within the timeout)
    in chronological order as [{'role': ..., 'content': ...}, ...]."""
    conn = _get_connection()
    cutoff = (datetime.utcnow() - timedelta(minutes=CONVERSATION_TIMEOUT_MINUTES)).isoformat()

    rows = conn.execute(
        """
        SELECT role, content FROM messages
        WHERE session_id = ? AND created_at >= ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, cutoff, limit)
    ).fetchall()
    conn.close()

    rows.reverse()  # sort oldest to newest
    return [{"role": role, "content": content} for role, content in rows]
