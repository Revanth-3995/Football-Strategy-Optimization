from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.config import settings
from backend.api.api import api_router

def get_application() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def health_check():
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Mount static charts directory
    os.makedirs("outputs/charts", exist_ok=True)
    application.mount("/charts", StaticFiles(directory="outputs/charts"), name="charts")

    return application

app = get_application()