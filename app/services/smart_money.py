from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from app.db import db_session


def _parse_time(value: str) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str) and value.isdigit():
        return datetime.utcfromtimestamp(int(value))
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compute_smart_money(
    min_roi: float = 0.2,
    min_win_rate: float = 0.6,
    min_trades: int = 5,
    since_days: int = 30,
) -> List[Dict[str, float]]:
    cutoff = datetime.utcnow() - timedelta(days=since_days)
    user_market_profit = defaultdict(float)
    user_stats = defaultdict(lambda: {"profit": 0.0, "stake": 0.0, "trade_count": 0})

    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT user_id, market_id, price, size, timestamp, profit
            FROM trades
            WHERE timestamp IS NOT NULL
            """
        ).fetchall()

    for row in rows:
        if row["timestamp"]:
            trade_time = _parse_time(row["timestamp"])
            if trade_time < cutoff:
                continue
        stake = (row["price"] or 0) * (row["size"] or 0)
        user_stats[row["user_id"]]["profit"] += row["profit"] or 0
        user_stats[row["user_id"]]["stake"] += abs(stake)
        user_stats[row["user_id"]]["trade_count"] += 1
        user_market_profit[(row["user_id"], row["market_id"])] += row["profit"] or 0

    results = []
    for user_id, stats in user_stats.items():
        if stats["trade_count"] < min_trades or stats["stake"] <= 0:
            continue
        market_profits = [
            profit for (uid, _), profit in user_market_profit.items() if uid == user_id
        ]
        if not market_profits:
            continue
        wins = sum(1 for profit in market_profits if profit > 0)
        win_rate = wins / len(market_profits)
        roi = stats["profit"] / stats["stake"] if stats["stake"] else 0
        if roi >= min_roi and win_rate >= min_win_rate:
            results.append(
                {
                    "user_id": user_id,
                    "roi": round(roi, 4),
                    "win_rate": round(win_rate, 4),
                    "profit": round(stats["profit"], 4),
                    "trade_count": stats["trade_count"],
                }
            )

    results.sort(key=lambda item: item["roi"], reverse=True)
    return results
