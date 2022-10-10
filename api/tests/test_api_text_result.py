def test_post_text_result_200(client, post_model, post_text):
    response = client.post(
        "/text_result/",
        json={
            "items": [{"text_result": [0.1, 1, 3], "text_sentence_id": 1, "model_id": 1}],
            "table_name": "table_1_source_1",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"message": "OK"}


def test_get_text_result_200(client, post_text, post_model):
    response = client.get("/text/sentences?sources=example.com&model_id=1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"items": [{"id": 1, "sentence": "string"}]}
    for _ in range(2):
        response = client.post(
            "/text_result/",
            json={
                "items": [{"text_result": [0.1, 1, 3], "text_sentence_id": data["items"][0]["id"], "model_id": 1}],
            },
        )
        assert response.status_code == 200, response.text
    response = client.get("/text_result/item/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {
        "items": [
            {
                "id": 1,
                "text_sentence_id": 1,
                "result": [0.1, 1, 3],
                "model_id": 1,
            },
            {
                "id": 2,
                "text_sentence_id": 1,
                "result": [0.1, 1, 3],
                "model_id": 1,
            },
        ]
    }


def post_text_result(client, items: dict):
    for item in items:
        response = client.post(
            "/text_result/",
            json={
                "items": [{"text_result": [0.1, 1, 3], "text_sentence_id": item["id"], "model_id": 1}],
            },
        )
        assert response.status_code == 200, response.text


def test_several_sources_and_models(client):
    for i in range(3):
        response = client.post(
            "/source/",
            json={"site": f"example{i}.com", "source_type": "review"},
        )
        assert response.status_code == 200, response.text
        response = client.post("/model/", json={"model_name": f"test_model{i}", "model_type": "test_type"})
        assert response.status_code == 200, response.text
        for j in range(10):
            response = client.post(
                "/text/",
                json={
                    "items": [
                        {
                            "source_id": i + 1,
                            "date": "2022-10-02T10:12:01.154Z",
                            "title": "string",
                            "text": "string",
                            "bank_id": "1000",
                            "link": "string",
                            "comments_num": 0,
                        }
                    ]
                },
            )
            assert response.status_code == 200, response.text
    response = client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1&limit=5")
    assert response.status_code == 200, response.text
    data = response.json()
    post_text_result(client, data["items"])
    for j in range(10):
        response = client.post(
            "/text/",
            json={
                "items": [
                    {
                        "source_id": 1,
                        "date": "2022-10-02T10:12:01.154Z",
                        "title": "string",
                        "text": "string",
                        "bank_id": "1000",
                        "link": "string",
                        "comments_num": 0,
                    }
                ]
            },
        )
        assert response.status_code == 200, response.text
    response = client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["items"]) == 25
    post_text_result(client, data["items"])
    response = client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1&limit=20")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["items"]) == 0
    post_text_result(client, data["items"])
    response = client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=2")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["items"]) == 30
