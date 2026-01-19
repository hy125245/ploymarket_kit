from fastapi import APIRouter

from app.scheduler import sync_markets, sync_trades, sync_users

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sync")
def sync_all():
    sync_trades()
    sync_markets()
    sync_users()
    return {"status": "ok"}
