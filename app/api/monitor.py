import os

from fastapi import APIRouter, Query

from app.services.smart_money import compute_smart_money, compute_suspicious_wallets
from app.services.whales import compute_whales

DEFAULT_ACCOUNT_AGE_DAYS = int(os.getenv("SUSPICIOUS_ACCOUNT_AGE_DAYS", "30"))
DEFAULT_LARGE_STAKE = float(os.getenv("SUSPICIOUS_LARGE_STAKE", "10000"))
DEFAULT_PROFIT_THRESHOLD = float(os.getenv("SUSPICIOUS_PROFIT_THRESHOLD", "10000"))
DEFAULT_REINVEST_MIN_DAYS = int(os.getenv("SUSPICIOUS_REINVEST_MIN_DAYS", "1"))
DEFAULT_REINVEST_MAX_DAYS = int(os.getenv("SUSPICIOUS_REINVEST_MAX_DAYS", "30"))

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/smart-money")
def smart_money():
    return {"data": compute_smart_money()}


@router.get("/whales")
def whales():
    return {"data": compute_whales()}


@router.get("/suspicious-wallets")
def suspicious_wallets(
    account_age_days: int = Query(DEFAULT_ACCOUNT_AGE_DAYS, ge=1),
    large_stake: float = Query(DEFAULT_LARGE_STAKE, ge=0),
    profit_threshold: float = Query(DEFAULT_PROFIT_THRESHOLD, ge=0),
    reinvest_min_days: int = Query(DEFAULT_REINVEST_MIN_DAYS, ge=0),
    reinvest_max_days: int = Query(DEFAULT_REINVEST_MAX_DAYS, ge=0),
):
    return {
        "data": compute_suspicious_wallets(
            account_age_days=account_age_days,
            large_stake=large_stake,
            profit_threshold=profit_threshold,
            reinvest_min_days=reinvest_min_days,
            reinvest_max_days=reinvest_max_days,
        )
    }
