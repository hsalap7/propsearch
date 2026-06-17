from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.properties import router as properties_router
from app.api.admin import router as admin_router
from app.core.config import settings
from app.core.dependencies import init_db_engine


async def _seed_sample_data(engine) -> None:
    """Insert sample Bangalore property listings when the table is empty."""
    import random
    from uuid import uuid4
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import func, select
    from app.models.property import Property

    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        count = await session.scalar(select(func.count()).select_from(Property))
        if count and count > 0:
            return  # already seeded

    LOCALITIES = {
        "Whitefield": (12.9698, 77.7499),
        "Bellandur": (12.9352, 77.6745),
        "HSR Layout": (12.9121, 77.6446),
        "Sarjapur": (12.8596, 77.7870),
        "Hebbal": (13.0358, 77.5970),
        "Indiranagar": (12.9716, 77.6412),
        "Electronic City": (12.8439, 77.6724),
        "Koramangala": (12.9352, 77.6245),
        "MG Road": (12.9789, 77.6155),
        "Marathahalli": (12.9591, 77.6974),
    }
    PROPERTY_TYPES = ["apartment", "villa", "townhouse", "independent house"]
    SOURCES = ["housing.com", "magicbricks.com", "nobroker.com", "99acres.com"]
    AMENITIES_POOL = [
        "gym", "pool", "parking", "security", "garden",
        "balcony", "elevator", "community center",
    ]

    async with Session() as session:
        for i in range(1, 101):
            locality = random.choice(list(LOCALITIES.keys()))
            base_lat, base_lng = LOCALITIES[locality]
            lat = base_lat + random.uniform(-0.012, 0.012)
            lng = base_lng + random.uniform(-0.012, 0.012)
            bedrooms = random.randint(1, 4)
            area = random.randint(500, 3000)
            ppsf = random.randint(4000, 9000)
            price = area * ppsf
            ptype = random.choice(PROPERTY_TYPES)
            source = random.choice(SOURCES)
            bathrooms = random.randint(1, max(1, bedrooms))

            images = [
                {"url": f"https://via.placeholder.com/400x300?text=Property+{i}+Image+{j}", "caption": f"View {j+1}"}
                for j in range(random.randint(2, 4))
            ]
            amenities = [
                {"name": a, "available": True}
                for a in random.sample(AMENITIES_POOL, random.randint(2, 5))
            ]
            location = f"POINT({lng} {lat})"

            prop = Property(
                id=str(uuid4()),
                source=source,
                external_id=f"{source}_{i}",
                title=f"{bedrooms} BHK {ptype.title()} in {locality}",
                description=(
                    f"Beautiful {bedrooms} BHK {ptype} in {locality}, Bangalore. "
                    f"Spread over {area} sq.ft with modern amenities. "
                    f"Well-connected to IT hubs, schools, and hospitals."
                ),
                property_type=ptype,
                price=price,
                price_per_sqft=ppsf,
                area_sqft=area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                address=f"{random.randint(100, 999)}, Main Road, {locality}, Bangalore",
                locality=locality,
                city="Bangalore",
                latitude=round(lat, 6),
                longitude=round(lng, 6),
                location=location,
                listing_url=f"https://example.com/property/{uuid4()}",
                image_urls=images,
                amenities=amenities,
                is_test_data=True,
            )
            session.add(prop)

        await session.commit()
        print(f"✅ Seeded 100 sample properties across {len(LOCALITIES)} localities")


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
    app.include_router(properties_router, prefix="/api/properties", tags=["properties"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    
    from app.api.ingest import router as ingest_router
    app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"])
    
    from app.api.analytics import router as analytics_router
    app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

    # Startup event
    @app.on_event("startup")
    async def startup():
        engine = await init_db_engine(settings.database_url)
        # Auto-seed with sample data if database is empty
        try:
            await _seed_sample_data(engine)
        except Exception as e:
            print(f"⚠️  Auto-seed skipped: {e}")

    return app


app = create_app()
