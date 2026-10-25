from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.storage import get_storage

settings = get_settings()

app = FastAPI(title="hireloop", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, limit_per_min=settings.shared_key_rate_limit_per_min)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": "hireloop"}


@app.get("/")
async def root() -> dict:
    return {"app": "hireloop", "status": "under construction"}


@app.on_event("startup")
def _init_storage() -> None:
    storage = get_storage()
    storage.create_all()
