import pytest


def test_post_model(client):
    response = client.post("/model/", json={"model_name": "test_model", "model_type": "test_type"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["model_id"] == 1


@pytest.mark.parametrize(
    "data", [{"model_name": "test_model"}, {"model_type": "test_type"}, {"model_name": 1, "qwer": "test_type"}]
)
def test_post_model_422(client, data):
    response = client.post("/model/", json=data)
    assert response.status_code == 422, response.text


def test_get_model_200(client, post_model):
    response = client.get("/model")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"items": [{"id": 1, "name": "test_model", "model_type_id": 1, "model_type": "test_type"}]}


def test_get_model_empty(client):
    response = client.get("/model")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"items": []}


def test_get_model_type_200(client, post_model):
    response = client.get("/model/type")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"items": [{"id": 1, "model_type": "test_type"}]}


def test_get_model_type_empty(client):
    response = client.get("/model/type")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"items": []}


def test_post_existing_model(client):
    model = {"model_name": "test_model", "model_type": "test_type"}
    response = client.post("/model/", json=model)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["model_id"] == 1
    response = client.post("/model/", json=model)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["model_id"] == 1
