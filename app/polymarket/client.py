import os
from typing import Any, Dict, List, Optional

import httpx

from app.db import db_session

DEFAULT_GAMMA_URL = "https://gamma-api.polymarket.com"
DEFAULT_DATA_URL = "https://data-api.polymarket.com"


class PolymarketClient:
    def __init__(
        self,
        gamma_url: Optional[str] = None,
        data_url: Optional[str] = None,
    ) -> None:
        self.gamma_url = gamma_url or os.getenv(
            "POLYMARKET_GAMMA_URL", DEFAULT_GAMMA_URL
        )
        self.data_url = data_url or os.getenv("POLYMARKET_DATA_URL", DEFAULT_DATA_URL)

    def get(
        self, base_url: str, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        response = httpx.get(f"{base_url}{path}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def fetch_markets(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        return self.get(
            self.gamma_url,
            "/markets",
            {
                "active": True,
                "closed": False,
                "limit": limit,
                "offset": offset,
                "order": "volume24hr",
                "ascending": False,
            },
        )

    def fetch_trades(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        return self.get(
            self.data_url,
            "/trades",
            {
                "limit": limit,
                "offset": offset,
            },
        )

    def fetch_users(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        return []


def upsert_trades(trades: List[Dict[str, Any]]) -> None:
    if not trades:
        return
    with db_session() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO trades
            (id, market_id, user_id, side, price, size, timestamp, profit, realized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    trade.get("transactionHash")
                    or trade.get("id")
                    or f"{trade.get('proxyWallet')}-{trade.get('timestamp')}-{trade.get('asset')}",
                    trade.get("conditionId"),
                    trade.get("proxyWallet"),
                    trade.get("side"),
                    trade.get("price"),
                    trade.get("size"),
                    trade.get("timestamp"),
                    trade.get("realizedPnl"),
                    1 if trade.get("realizedPnl") else 0,
                )
                for trade in trades
            ],
        )


def upsert_markets(markets: List[Dict[str, Any]]) -> None:
    if not markets:
        return
    with db_session() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO markets
            (id, question, volume_24h, volume, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    market.get("conditionId") or market.get("id"),
                    market.get("question"),
                    market.get("volume24hr"),
                    market.get("volume"),
                    "active" if market.get("active") else "closed",
                    market.get("createdAt"),
                )
                for market in markets
            ],
        )


def upsert_users(users: List[Dict[str, Any]]) -> None:
    if not users:
        return
    with db_session() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO users
            (id, address)
            VALUES (?, ?)
            """,
            [(user.get("id"), user.get("address")) for user in users],
        )
