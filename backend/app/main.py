from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes
from .core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"app": settings.app_name}
