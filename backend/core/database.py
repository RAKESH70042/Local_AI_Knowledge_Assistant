"""
database.py
-----------
Saves every Q&A to a local SQLite database.
Gives you full chat history like ChatGPT — stored on your PC.
"""

import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DB_PATH = "./data/chat_history.db"


# ── Connection ────────────────────────────────────────────────────────────────

def get_connection():
    os.makedirs("./data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Create Tables ─────────────────────────────────────────────────────────────

def create_tables():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            question   TEXT NOT NULL,
            answer     TEXT NOT NULL,
            sources    TEXT,
            latency    REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── Save Chat ─────────────────────────────────────────────────────────────────

def save_chat(question: str, answer: str, sources: list, latency: float):
    """Save a Q&A pair to the database."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO chats (question, answer, sources, latency, created_at) VALUES (?,?,?,?,?)",
        (
            question,
            answer,
            ", ".join(sources) if sources else "",
            latency,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    conn.commit()
    conn.close()


# ── Read Chats ────────────────────────────────────────────────────────────────

def get_all_chats() -> list:
    """Return all chats ordered by newest first."""
    conn  = get_connection()
    rows  = conn.execute(
        "SELECT * FROM chats ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_chats(keyword: str) -> list:
    """Search chats by keyword in question or answer."""
    conn  = get_connection()
    rows  = conn.execute(
        "SELECT * FROM chats WHERE question LIKE ? OR answer LIKE ? ORDER BY created_at DESC",
        (f"%{keyword}%", f"%{keyword}%")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Delete Chats ──────────────────────────────────────────────────────────────

def delete_chat(chat_id: int):
    """Delete a single chat by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM chats WHERE id=?", (chat_id,))
    conn.commit()
    conn.close()


def clear_all_chats():
    """Delete all chat history."""
    conn = get_connection()
    conn.execute("DELETE FROM chats")
    conn.commit()
    conn.close()


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_stats() -> dict:
    """Return total questions asked and average response time."""
    conn  = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    avg   = conn.execute("SELECT AVG(latency) FROM chats").fetchone()[0]
    conn.close()
    return {
        "total_questions":    total,
        "avg_latency_seconds": round(avg or 0, 2)
    }


# ── Auto create tables on import ──────────────────────────────────────────────
create_tables()
# ── ChatDatabase wrapper (used by main.py) ────────────────────────────────────
 
class ChatDatabase:
    def __init__(self, db_path):
        global DB_PATH
        DB_PATH = str(db_path)
        create_tables()
 
    def save_message(self, session_id: str, role: str, content: str):
        """Map main.py's save_message() call to the existing save_chat()."""
        save_chat(
            question=content if role == "user" else "",
            answer=content if role == "assistant" else "",
            sources=[],
            latency=0,
        )
 

# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nDB path: {DB_PATH}\n")

    print("Saving test chat...")
    save_chat(
        question="When was Acme Corp founded?",
        answer="Acme Corp was founded in 2015 in Bangalore.",
        sources=["test.txt"],
        latency=1.2
    )

    chats = get_all_chats()
    print(f"  ✓ Total chats saved: {len(chats)}")
    print(f"  ✓ Latest: {chats[0]['question']}")
    print(f"  ✓ Stats:  {get_stats()}")
    print("\nDatabase working correctly!")