from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.db import db_session
from app.services.smart_money import compute_realized_profits, load_trades


def _parse_time(value: str) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str) and value.isdigit():
        return datetime.utcfromtimestamp(int(value))
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def top_profit(limit: int = 20, since_days: int = 30) -> List[Dict[str, float]]:
    cutoff = datetime.utcnow() - timedelta(days=since_days)
    totals: Dict[str, float] = {}

    trades = load_trades()
    profits = compute_realized_profits(trades)

    for entry in profits:
        if entry["timestamp"] < cutoff:
            continue
        totals[entry["user_id"]] = totals.get(entry["user_id"], 0.0) + entry["profit"]

    rankings = [
        {"user_id": user_id, "profit": round(total, 4)}
        for user_id, total in totals.items()
    ]
    rankings.sort(key=lambda item: item["profit"], reverse=True)
    return rankings[:limit]
