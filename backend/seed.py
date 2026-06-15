"""Seed script to populate sample Bangalore property data."""

import asyncio
import random
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.property import Property
from app.db.session import Base
from app.schemas.property import PropertyCreate
from app.services.property import PropertyService

# Bangalore localities with approximate coordinates
LOCALITIES = {
    "Whitefield": (12.9698, 77.7499),
    "Bellandur": (12.9352, 77.6245),
    "HSR Layout": (12.9352, 77.6245),
    "Sarjapur": (12.8196, 77.6548),
    "Hebbal": (13.0016, 77.5699),
    "Indiranagar": (12.9716, 77.6412),
    "Electronic City": (12.8439, 77.6724),
    "Koramangala": (12.9352, 77.6245),
    "MG Road": (12.9789, 77.6155),
    "Marathahalli": (12.9689, 77.6994),
}

PROPERTY_TYPES = ["apartment", "villa", "townhouse", "independent house"]
AMENITIES = [
    "gym",
    "pool",
    "parking",
    "security",
    "garden",
    "balcony",
    "elevator",
    "community center",
]
SOURCES = ["housing.com", "magicbricks.com", "nobroker.com"]


def generate_property_data(index: int) -> dict:
    """Generate random property data."""
    locality = random.choice(list(LOCALITIES.keys()))
    base_lat, base_lng = LOCALITIES[locality]
    
    # Add some randomness to coordinates
    latitude = base_lat + random.uniform(-0.01, 0.01)
    longitude = base_lng + random.uniform(-0.01, 0.01)
    
    bedrooms = random.randint(1, 4)
    area_sqft = random.randint(500, 3000)
    price_per_sqft = random.randint(3000, 8000)
    total_price = area_sqft * price_per_sqft
    
    property_type = random.choice(PROPERTY_TYPES)
    source = random.choice(SOURCES)
    
    # Generate image URLs using placeholder service
    images = [
        {"url": f"https://via.placeholder.com/400x300?text=Property+Image+{i}", "caption": f"Image {i+1}"}
        for i in range(random.randint(2, 5))
    ]
    
    # Select random amenities
    property_amenities = [
        {"name": amenity, "available": True}
        for amenity in random.sample(AMENITIES, random.randint(2, 5))
    ]
    
    return {
        "source": source,
        "external_id": f"{source}_{index}",
        "title": f"{bedrooms} BHK {property_type.title()} in {locality}",
        "description": f"Beautiful {property_type} with {bedrooms} bedrooms and {random.randint(1, 3)} bathrooms in {locality}. "
                      f"Well-maintained property with modern amenities.",
        "property_type": property_type,
        "price": total_price,
        "price_per_sqft": price_per_sqft,
        "area_sqft": area_sqft,
        "bedrooms": bedrooms,
        "bathrooms": random.randint(1, bedrooms),
        "address": f"{random.randint(100, 999)} Main Street, {locality}",
        "locality": locality,
        "city": "Bangalore",
        "latitude": latitude,
        "longitude": longitude,
        "listing_url": f"https://example.com/property/{uuid4()}",
        "image_urls": images,
        "amenities": property_amenities,
    }


async def seed_data(database_url: str, count: int = 100):
    """Seed the database with sample properties."""
    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Seed data
    async with async_session() as session:
        service = PropertyService(session)
        
        print(f"🌱 Seeding {count} properties...")
        
        for i in range(1, count + 1):
            try:
                property_data = generate_property_data(i)
                property_schema = PropertyCreate(**property_data)
                
                await service.create_property(property_schema)
                
                if i % 10 == 0:
                    print(f"   ✓ Created {i}/{count} properties")
            except Exception as e:
                print(f"   ✗ Error creating property {i}: {e}")
                continue
        
        print(f"✅ Seeding complete! {count} properties added.")
    
    await engine.dispose()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://propertydb:propertydb_password@localhost:5432/propsearch"
    )
    
    # Convert to async database URL if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    asyncio.run(seed_data(database_url, count=100))
