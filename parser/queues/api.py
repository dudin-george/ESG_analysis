import requests
import json
from settings import Settings
from shemes.bank import Bank, Source, SourceResponse, TextRequest

URL = Settings().api_url


def get_bank_list() -> list[Bank]:
    r = requests.get(URL + "/bank")
    banks = [Bank(**bank) for bank in r.json()["items"]]
    return banks


def send_source(source: Source) -> int:
    r = requests.post(URL + "/source", json=source.dict())
    if r.status_code != 200:
        print(r.json())
        raise Exception("Error send source")
    return int(r.json()["source_id"])


def get_source_by_id(source_id: int) -> SourceResponse:
    r = requests.get(URL + f"/source/{source_id}")
    return SourceResponse(**r.json())


def send_texts(text: TextRequest) -> None:
    items = []
    for item in text.items:
        d = item.dict()
        d["date"] = d["date"].isoformat()
        items.append(d)
    request = {"items": items, "last_update": text.last_update.isoformat()}
    r = requests.post(URL + "/text", json=request)
    if r.status_code != 200:
        print(r.json())
        raise Exception("Error send text")
