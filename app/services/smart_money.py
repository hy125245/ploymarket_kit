from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from app.db import db_session


def _parse_time(value: str) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str) and value.isdigit():
        return datetime.utcfromtimestamp(int(value))
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_trades() -> List[Dict[str, Any]]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT user_id, market_id, side, price, size, timestamp
            FROM trades
            WHERE timestamp IS NOT NULL
            """
        ).fetchall()

    trades: List[Dict[str, Any]] = []
    for row in rows:
        trade_time = _parse_time(row["timestamp"])
        trades.append(
            {
                "user_id": row["user_id"],
                "market_id": row["market_id"],
                "side": row["side"],
                "price": row["price"],
                "size": row["size"],
                "timestamp": trade_time,
            }
        )
    return trades


def compute_realized_profits(
    trades: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[(trade["user_id"], trade["market_id"])].append(trade)

    profits: List[Dict[str, Any]] = []
    for (user_id, market_id), market_trades in grouped.items():
        market_trades.sort(key=lambda item: item["timestamp"])
        position = 0.0
        cost = 0.0

        for trade in market_trades:
            side = (trade.get("side") or "").upper()
            price = trade.get("price") or 0
            size = trade.get("size") or 0
            if size <= 0:
                continue

            if side == "BUY":
                position += size
                cost += price * size
                continue

            if side != "SELL":
                continue

            if position <= 0:
                continue

            cost_per_unit = cost / position if position else 0
            realized_size = min(size, position)
            profit = (price - cost_per_unit) * realized_size
            if realized_size > 0:
                profits.append(
                    {
                        "user_id": user_id,
                        "market_id": market_id,
                        "timestamp": trade["timestamp"],
                        "profit": profit,
                    }
                )
            position -= realized_size
            cost = cost_per_unit * position

    return profits


def compute_smart_money(
    min_roi: float = 0.2,
    min_win_rate: float = 0.6,
    min_trades: int = 5,
    since_days: int = 30,
) -> List[Dict[str, float]]:
    cutoff = datetime.utcnow() - timedelta(days=since_days)
    user_market_profit = defaultdict(float)
    user_stats = defaultdict(lambda: {"profit": 0.0, "stake": 0.0, "trade_count": 0})

    trades = load_trades()
    profits = compute_realized_profits(trades)

    for trade in trades:
        if trade["timestamp"] < cutoff:
            continue
        stake = (trade["price"] or 0) * (trade["size"] or 0)
        user_stats[trade["user_id"]]["stake"] += abs(stake)
        user_stats[trade["user_id"]]["trade_count"] += 1

    for entry in profits:
        if entry["timestamp"] < cutoff:
            continue
        user_stats[entry["user_id"]]["profit"] += entry["profit"]
        user_market_profit[(entry["user_id"], entry["market_id"])] += entry["profit"]

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
