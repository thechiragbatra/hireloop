from fastapi import APIRouter

from . import apply_kit, health, jobs, pipeline, tailor, tracker, upload

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(tailor.router, tags=["tailor"])
api_router.include_router(tracker.router, tags=["tracker"])
api_router.include_router(pipeline.router, tags=["pipeline"])
api_router.include_router(apply_kit.router, tags=["apply-kit"])
