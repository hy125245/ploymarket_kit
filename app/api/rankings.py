from fastapi import APIRouter

from app.services.rankings import top_profit

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/top-profit")
def top_profit_rankings():
    return {"data": top_profit()}
