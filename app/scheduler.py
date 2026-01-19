import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.polymarket.client import (
    PolymarketClient,
    upsert_markets,
    upsert_trades,
    upsert_users,
)

logger = logging.getLogger(__name__)


def sync_trades(client: Optional[PolymarketClient] = None) -> None:
    client = client or PolymarketClient()
    try:
        trades = client.fetch_trades()
        upsert_trades(trades)
    except Exception as exc:
        logger.error("Failed to sync trades: %s", exc)


def sync_markets(client: Optional[PolymarketClient] = None) -> None:
    client = client or PolymarketClient()
    try:
        markets = client.fetch_markets()
        upsert_markets(markets)
    except Exception as exc:
        logger.error("Failed to sync markets: %s", exc)


def sync_users(client: Optional[PolymarketClient] = None) -> None:
    client = client or PolymarketClient()
    try:
        users = client.fetch_users()
        upsert_users(users)
    except Exception as exc:
        logger.error("Failed to sync users: %s", exc)


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_trades, "interval", minutes=10, id="sync_trades")
    scheduler.add_job(sync_markets, "interval", hours=1, id="sync_markets")
    scheduler.add_job(sync_users, "interval", hours=6, id="sync_users")
    scheduler.start()
    return scheduler
