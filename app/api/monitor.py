from fastapi import APIRouter

from app.services.smart_money import compute_smart_money
from app.services.whales import compute_whales

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/smart-money")
def smart_money():
    return {"data": compute_smart_money()}


@router.get("/whales")
def whales():
    return {"data": compute_whales()}
