import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def fix():
    engine = create_async_engine("postgresql+asyncpg://propertydb:propertydb_password@postgres:5432/propsearch")
    async with engine.begin() as conn:
        await conn.execute(text("""
            UPDATE properties
            SET image_urls = (
                SELECT jsonb_agg(
                    CASE 
                        WHEN jsonb_typeof(elem) = 'string' THEN jsonb_build_object('url', elem)
                        ELSE elem
                    END
                )
                FROM jsonb_array_elements(image_urls::jsonb) AS elem
            )
            WHERE image_urls IS NOT NULL AND jsonb_typeof(image_urls::jsonb) = 'array'
            AND EXISTS (
                SELECT 1 FROM jsonb_array_elements(image_urls::jsonb) AS elem
                WHERE jsonb_typeof(elem) = 'string'
            );
        """))
        await conn.execute(text("""
            UPDATE properties
            SET amenities = (
                SELECT jsonb_agg(
                    CASE 
                        WHEN jsonb_typeof(elem) = 'string' THEN jsonb_build_object('name', elem, 'available', true)
                        ELSE elem
                    END
                )
                FROM jsonb_array_elements(amenities::jsonb) AS elem
            )
            WHERE amenities IS NOT NULL AND jsonb_typeof(amenities::jsonb) = 'array'
            AND EXISTS (
                SELECT 1 FROM jsonb_array_elements(amenities::jsonb) AS elem
                WHERE jsonb_typeof(elem) = 'string'
            );
        """))
        print("Fixed image_urls and amenities")

asyncio.run(fix())
