from fastapi import APIRouter

from backend.api import matches, competitions, analytics, visualizations, ml, tactical

api_router = APIRouter()
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(visualizations.router, prefix="/visualizations", tags=["visualizations"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(tactical.router, prefix="/tactical", tags=["tactical"])

