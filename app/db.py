import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_PATH = os.getenv(
    "DATABASE_URL", "/home/hy125245/ploymarket/ploymarket_kit/polymarket.db"
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db_session() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                market_id TEXT,
                user_id TEXT,
                side TEXT,
                price REAL,
                size REAL,
                timestamp TEXT,
                profit REAL,
                realized INTEGER DEFAULT 0
            )
                        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS markets (
                id TEXT PRIMARY KEY,
                question TEXT,
                volume_24h REAL,
                volume REAL,
                status TEXT,
                created_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                address TEXT
            )
            """
        )
