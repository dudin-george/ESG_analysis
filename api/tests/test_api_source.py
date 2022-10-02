import pytest


@pytest.fixture
def post_source(client) -> None:
    response = client.post(
        "/source/",
        json={"site": "example.com", "source_type": "review"},
    )
    assert response.status_code == 200, response.text


@pytest.mark.parametrize(
    "data",
    [
        {"site": "example.com", "source_type": "review"},
    ],
)
def test_post_source_200(client, data):
    response = client.post(
        "/source/",
        json=data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["source_id"] == 1


@pytest.mark.parametrize(
    "data",
    [
        {"site": "example.com"},
        {"source_type": "example.com"},
        {"sitea": 1, "source_type": "review"},
    ],
)
def test_post_source_422(client, data):
    response = client.post(
        "/source/",
        json=data,
    )
    assert response.status_code == 422, response.text


def test_get_source_200(client, post_source):
    response = client.get("/source")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {
        "items": [{"id": 1, "site": "example.com", "source_type_id": 1, "last_update": None, "parser_state": None}]
    }


def test_get_source_item_200(client, post_source):
    response = client.get("/source/item/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {
        "id": 1,
        "site": "example.com",
        "source_type_id": 1,
        "last_update": None,
        "parser_state": None,
    }


def test_get_source_404(client):
    response = client.get("/source")
    assert response.status_code == 200, response.text
    assert response.json() == {"items": []}


def test_get_source_item_404(client):
    response = client.get("/source/item/1")
    assert response.status_code == 404, response.text


def test_get_source_type(client, post_source):
    response = client.post(
        "/source/",
        json={"site": "example2.com", "source_type": "news"},
    )
    assert response.status_code == 200, response.text
    response = client.get("/source/type")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "items": [
            {"id": 1, "name": "review"},
            {"id": 2, "name": "news"},
        ]
    }
