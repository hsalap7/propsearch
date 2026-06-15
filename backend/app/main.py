from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.properties import router as properties_router
from app.core.config import settings
from app.core.dependencies import init_db_engine


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Property Search API",
        description="API for Bangalore real estate property search",
        version="1.0.0",
        debug=settings.fastapi_debug,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router)
    app.include_router(properties_router)

    # Startup event
    @app.on_event("startup")
    async def startup():
        await init_db_engine(settings.database_url)

    return app


app = create_app()
