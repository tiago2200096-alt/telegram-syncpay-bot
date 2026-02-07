# app/media_store.py
import os
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

DB_PATH = os.getenv("DB_PATH", "bot.db")

def _conn():
    return sqlite3.connect(DB_PATH)

def init_media_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS media_assets (
            key TEXT PRIMARY KEY,
            file_id TEXT NOT NULL,
            media_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        con.commit()

def upsert_media(key: str, file_id: str, media_type: str):
    key = key.strip().upper()
    with _conn() as con:
        con.execute("""
        INSERT INTO media_assets(key, file_id, media_type, created_at)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            file_id=excluded.file_id,
            media_type=excluded.media_type,
            created_at=excluded.created_at
        """, (key, file_id, media_type, datetime.utcnow().isoformat()))
        con.commit()

def get_media(key: str) -> Optional[Tuple[str, str]]:
    key = key.strip().upper()
    with _conn() as con:
        cur = con.execute("SELECT file_id, media_type FROM media_assets WHERE key=?", (key,))
        row = cur.fetchone()
        return row if row else None
