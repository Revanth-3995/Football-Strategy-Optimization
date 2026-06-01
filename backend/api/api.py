from fastapi import APIRouter

from backend.api import matches, competitions, analytics

api_router = APIRouter()
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
