from datetime import datetime, timedelta
from typing import Dict, List

from app.db import db_session


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compute_whales(min_net_invested: float = 10000.0, since_hours: int = 24) -> List[Dict[str, float]]:
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    totals: Dict[str, float] = {}

    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT user_id, price, size, timestamp
            FROM trades
            WHERE timestamp IS NOT NULL
            """
        ).fetchall()

    for row in rows:
        trade_time = _parse_time(row["timestamp"])
        if trade_time < cutoff:
            continue
        stake = abs((row["price"] or 0) * (row["size"] or 0))
        totals[row["user_id"]] = totals.get(row["user_id"], 0.0) + stake

    whales = [
        {"user_id": user_id, "net_invested": round(total, 4)}
        for user_id, total in totals.items()
        if total >= min_net_invested
    ]
    whales.sort(key=lambda item: item["net_invested"], reverse=True)
    return whales
