import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_empty_properties(client: AsyncClient):
    """Test listing properties when none exist."""
    response = await client.get("/api/properties/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["limit"] == 50
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_list_properties_with_pagination(client: AsyncClient):
    """Test properties pagination."""
    response = await client.get("/api/properties/?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_get_nonexistent_property(client: AsyncClient):
    """Test getting a property that doesn't exist."""
    response = await client.get("/api/properties/nonexistent-id")
    assert response.status_code == 404
