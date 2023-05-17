import pytest
import requests
import vcr

from app.dataloader import BankParser

my_vcr = vcr.VCR(
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    serializer="yaml",
    cassette_library_dir="cassettes/",
    match_on=("method", "scheme", "host", "port", "path"),
)

@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_bank_page():
    data = requests.get(BankParser.BASE_PAGE_URL)
    return BankParser.BASE_PAGE_URL, data.text

@pytest.fixture
def get_cbr_bank_page_mock(mock_request, get_cbr_bank_page):
    url, page = get_cbr_bank_page
    mock_request.get(url, text=page)
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_bank_file(get_cbr_bank_page):
    _, page = get_cbr_bank_page
    file_url = BankParser.get_dataframe_url(page)
    data = requests.get(file_url)
    return file_url, data.content

@pytest.fixture
def get_cbr_bank_file_mock(mock_request, get_cbr_bank_file):
    url, content = get_cbr_bank_file
    mock_request.get(url, content=content)
    yield mock_request
