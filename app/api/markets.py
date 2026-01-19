from fastapi import APIRouter

from app.services.hot_markets import hot_markets

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/hot")
def hot_market_list():
    return {"data": hot_markets()}
