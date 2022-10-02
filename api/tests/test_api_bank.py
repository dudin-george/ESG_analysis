from fastapi.testclient import TestClient


def test_get_bank(client: TestClient) -> None:
    response = client.get("/bank")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 300
    assert data["items"][0].get("id", None) is not None
    assert data["items"][0].get("bank_name", None) is not None
