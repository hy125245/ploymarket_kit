import os
from typing import Any, Dict, List, Optional

import httpx

from app.db import db_session
from app.polymarket.queries import MARKETS_QUERY, TRADES_QUERY, USERS_QUERY

DEFAULT_GRAPHQL_URL = "https://gamma-api.polymarket.com/graphql"


class PolymarketClient:
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.endpoint = endpoint or os.getenv("POLYMARKET_GRAPHQL_URL", DEFAULT_GRAPHQL_URL)
        self.api_key = api_key or os.getenv("POLYMARKET_API_KEY")

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"query": query, "variables": variables or {}}
        response = httpx.post(self.endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        return data.get("data", {})

    def fetch_trades(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        data = self.execute(TRADES_QUERY, {"limit": limit, "offset": offset})
        return data.get("trades", [])

    def fetch_markets(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        data = self.execute(MARKETS_QUERY, {"limit": limit, "offset": offset})
        return data.get("markets", [])

    def fetch_users(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        data = self.execute(USERS_QUERY, {"limit": limit, "offset": offset})
        return data.get("users", [])


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
                    trade.get("id"),
                    trade.get("marketId"),
                    trade.get("userId"),
                    trade.get("side"),
                    trade.get("price"),
                    trade.get("size"),
                    trade.get("createdAt"),
                    trade.get("profit"),
                    1 if trade.get("realized") else 0,
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
                    market.get("id"),
                    market.get("question"),
                    market.get("volume24h"),
                    market.get("volume"),
                    market.get("status"),
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
