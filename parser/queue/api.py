import requests

from settings import Settings
from shemes.bank import Bank, Source, SourceResponse, TextRequest

URL = Settings().api_url


def get_bank_list() -> list[Bank]:
    r = requests.get(URL + "/bank")
    return r.json()["items"]


def send_source(source: Source) -> int:
    r = requests.post(URL + "/source", json=source.dict())
    return r.json()["source_id"]


def get_source_by_id(source_id: int) -> SourceResponse:
    r = requests.get(URL + f"/source/{source_id}")
    return r.json()


def send_texts(text: TextRequest) -> None:
    requests.post(URL + "/text", json=text.dict())
