import pytest
import vcr
import requests
import requests_mock

my_vcr = vcr.VCR(
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    serializer="yaml",
    cassette_library_dir="vcr_cassettes",
)

@pytest.fixture(scope="session")
@my_vcr.use_cassette
def sravni_banks_list() -> tuple[str, dict]:
    url = "https://www.sravni.ru/proxy-organizations/organizations"
    params = {"active": True, "limit": 400, "organizationType": "bank", "skip": 0}
    return (
        url,
        requests.get(url, params=params).json(),
    )

@pytest.fixture(scope="session")
@my_vcr.use_cassette
def bank_sravni_reviews_response() -> tuple[str, dict]:
    params = {
        "filterBy": "withRates",
        "isClient": False,
        "locationRoute": None,
        "newIds": True,
        "orderBy": "byDate",
        "pageIndex": 1,
        "pageSize": 10,
        "reviewObjectId": "5bb4f768245bc22a520a6115",
        "reviewObjectType": "bank",
        "specificProductId": None,
        "tag": None,
        "withVotes": True,
    }
    url = "https://www.sravni.ru/proxy-reviews/reviews/"
    return (
        url,
        requests.get("https://www.sravni.ru/proxy-reviews/reviews/", params=params).json(),
    )


@pytest.fixture
def mock_sravni_bank_reviews_response(mock_request, bank_sravni_reviews_response) -> requests_mock.Mocker:
    mock_request.get(bank_sravni_reviews_response[0], json=bank_sravni_reviews_response[1])
    yield mock_request


@pytest.fixture
def mock_sravni_banks_list(mock_request, sravni_banks_list) -> requests_mock.Mocker:
    mock_request.get(sravni_banks_list[0], json=sravni_banks_list[1])
    yield mock_request
