from datetime import datetime, timedelta
from typing import Dict, List

from app.db import db_session


def _parse_time(value: str) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str) and value.isdigit():
        return datetime.utcfromtimestamp(int(value))
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def hot_markets(limit: int = 20, since_hours: int = 24) -> List[Dict[str, float]]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT id, question, volume_24h
            FROM markets
            WHERE volume_24h IS NOT NULL
            """
        ).fetchall()

    if rows:
        markets = [
            {
                "market_id": row["id"],
                "question": row["question"],
                "volume": row["volume_24h"],
            }
            for row in rows
        ]
        markets.sort(key=lambda item: item["volume"] or 0, reverse=True)
        return markets[:limit]

    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    totals: Dict[str, float] = {}
    questions: Dict[str, str] = {}

    with db_session() as conn:
        trade_rows = conn.execute(
            """
            SELECT market_id, price, size, timestamp
            FROM trades
            WHERE timestamp IS NOT NULL
            """
        ).fetchall()
        market_rows = conn.execute("SELECT id, question FROM markets").fetchall()

    for row in market_rows:
        questions[row["id"]] = row["question"]

    for row in trade_rows:
        if _parse_time(row["timestamp"]) < cutoff:
            continue
        volume = abs((row["price"] or 0) * (row["size"] or 0))
        totals[row["market_id"]] = totals.get(row["market_id"], 0.0) + volume

    markets = [
        {
            "market_id": market_id,
            "question": questions.get(market_id),
            "volume": round(total, 4),
        }
        for market_id, total in totals.items()
    ]
    markets.sort(key=lambda item: item["volume"], reverse=True)
    return markets[:limit]
