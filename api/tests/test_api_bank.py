import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_bank(client: AsyncClient) -> None:
    response = await client.get("/bank/")
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0].get("id", None) is not None
    assert data["items"][0].get("bank_name", None) is not None
