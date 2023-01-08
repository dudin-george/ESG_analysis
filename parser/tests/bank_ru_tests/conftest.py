import re
from typing import Any

import pytest
import requests
import requests_mock
import vcr


@pytest.fixture
def bank_reviews_response_fixed() -> tuple[str, dict]:
    return "https://www.banki.ru/services/responses/list/ajax/", {
        "data": [
            {
                "id": 10721721,
                "dateCreate": "2022-10-08 16:05:01",
                "text": "<p>Клиент Юникредита c с…онков, ни сообщений.</p>",
                "title": "<p>Клиент Юникредита c с…онков, ни сообщений.</p>",
                "grade": 1,
                "isCountable": True,
                "resolutionIsApproved": None,
                "commentCount": 4,
                "company": {
                    "id": 4045,
                    "code": "unicreditbank",
                    "name": "unicreditbank",
                    "url": "unicreditbank",
                },
            },
            {
                "id": 10720416,
                "dateCreate": "2021-10-04 15:46:32",
                "text": (
                    "Сегодня выяснилась еще одна новинка от ЮниКредит Банк. На сайте банка публикуется одна ставка, но"
                ),
                "title": "Ставки на сайте банка не…ствуют действительности",
                "grade": 1,
                "isCountable": True,
                "resolutionIsApproved": None,
                "commentCount": 4,
                "company": {
                    "id": 4045,
                    "code": "unicreditbank",
                    "name": "unicreditbank",
                    "url": "unicreditbank",
                },
            },
        ],
        "total": 2,
    }


@pytest.fixture(scope="session")
@vcr.use_cassette("vcr_cassettes/banki_banks_list.yaml")
def banki_banks_list() -> tuple[str, dict]:
    url = "https://www.banki.ru/widget/ajax/bank_list.json"
    return (
        url,
        requests.get(url).json(),
    )


@pytest.fixture(scope="session")
@vcr.use_cassette("vcr_cassettes/bank_reviews_response.yaml")
def bank_reviews_response() -> tuple[str, dict]:
    url = "https://www.banki.ru/services/responses/list/ajax/"
    return (
        url,
        requests.get(
            url, params={"page": 1, "bank": "unicreditbank"}
        ).json(),
    )


@pytest.fixture
def mock_bank_reviews_response(mock_request, bank_reviews_response) -> requests_mock.Mocker:
    mock_request.get(bank_reviews_response[0], json=bank_reviews_response[1])
    yield mock_request


@pytest.fixture
def mock_banki_ru_banks_list(mock_request, banki_banks_list) -> requests_mock.Mocker:
    mock_request.get(banki_banks_list[0], json=banki_banks_list[1])
    yield mock_request

broker_list_url = "https://www.banki.ru/investment/brokers/list/"
@vcr.use_cassette("vcr_cassettes/get_broker_list.yaml")
def get_broker_list() -> dict[str, Any]:
    return requests.get(
        broker_list_url, headers={"x-requested-with": "XMLHttpRequest"}
    ).json()


broker_banki_list = get_broker_list()


@pytest.fixture(scope="session")
def banki_brokers_list_with_header() -> tuple[str, dict]:
    return broker_list_url, broker_banki_list


@pytest.fixture
def mock_banki_ru_brokers_list(mock_request, banki_brokers_list_with_header) -> requests_mock.Mocker:
    mock_request.get(banki_brokers_list_with_header[0], json=banki_brokers_list_with_header[1])
    yield mock_request


def json_response_for_broker(request, context):
    dict_response = {
        "creditsuisse": {"licence": "045-02972-100000"},
        "crescofinance": {"licence": "045-12685-100000"},
        "generalinvest": {"licence": "177-12660-100000, 177-12670-001000"},
    }
    name = request.path_url.split("/")[-2]
    match name:
        case "list":
            return broker_banki_list
        case _ if name in dict_response.keys():
            return {"data": {"broker": dict_response[name]}}
        case _:
            return {"message": "Not found"}


@pytest.fixture
def mock_banki_ru_brokers_license(mock_request, banki_brokers_list_with_header) -> requests_mock.Mocker:
    pattern = re.compile(r"https://www.banki.ru/investment/brokers/(.+)/")
    mock_request.get(pattern, json=json_response_for_broker)
    yield mock_request


@pytest.fixture(scope="session")
@vcr.use_cassette("vcr_cassettes/broker_page.yaml")
def broker_page() -> str:
    return requests.get("https://www.banki.ru/investment/responses/company/broker/alfa-direkt/").text


@pytest.fixture
def mock_broker_page(mock_request, broker_page) -> requests_mock.Mocker:
    pattern = re.compile(r"https://www.banki.ru/investment/responses/company/broker/(.+)/")
    mock_request.get(pattern, text=broker_page)
    yield mock_request
