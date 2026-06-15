import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_stats_empty(client: AsyncClient):
    response = await client.get("/admin/stats")
    assert response.status_code == 200
    assert response.json() == {
        "properties": 0,
        "duplicates": 0,
        "housing": 0,
        "nobroker": 0,
        "magicbricks": 0,
        "99acres": 0,
    }
