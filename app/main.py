import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.markets import router as markets_router
from app.api.monitor import router as monitor_router
from app.api.rankings import router as rankings_router
from app.db import init_db
from app.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Polymarket Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitor_router)
app.include_router(rankings_router)
app.include_router(markets_router)
app.include_router(admin_router)


@app.get("/demo")
def demo():
    return {"status": "ok", "message": "demo endpoint"}


@app.on_event("startup")
def startup() -> None:
    init_db()
    start_scheduler()
