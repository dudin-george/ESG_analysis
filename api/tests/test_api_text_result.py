def test_post_text_result_200(client, post_model, post_text):
    response = client.post("/text_result/", json=[{"text_result": [0.1, 1, 3], "text_sentence_id": 1, "model_id": 1}])
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"message": "OK"}


def test_get_text_result_200(client, post_text, post_model):
    for _ in range(2):
        response = client.post(
            "/text_result/", json=[{"text_result": [0.1, 1, 3], "text_sentence_id": 1, "model_id": 1}]
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
