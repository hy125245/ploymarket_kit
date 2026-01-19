from datetime import datetime, timedelta
from typing import Dict, List

from app.db import db_session


def _parse_time(value: str) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str) and value.isdigit():
        return datetime.utcfromtimestamp(int(value))
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def top_profit(limit: int = 20, since_days: int = 30) -> List[Dict[str, float]]:
    cutoff = datetime.utcnow() - timedelta(days=since_days)
    totals: Dict[str, float] = {}

    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT user_id, timestamp, profit, realized
            FROM trades
            WHERE timestamp IS NOT NULL AND realized = 1
            """
        ).fetchall()

    for row in rows:
        if _parse_time(row["timestamp"]) < cutoff:
            continue
        totals[row["user_id"]] = totals.get(row["user_id"], 0.0) + (row["profit"] or 0)

    rankings = [
        {"user_id": user_id, "profit": round(total, 4)}
        for user_id, total in totals.items()
    ]
    rankings.sort(key=lambda item: item["profit"], reverse=True)
    return rankings[:limit]
