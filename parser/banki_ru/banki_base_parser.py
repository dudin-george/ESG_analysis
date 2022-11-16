from typing import Any

import requests

from banki_ru.queries import get_bank_list
from common.base_parser import BaseParser
from common.schemes import Source


class BankiBase(BaseParser):
    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        self.source = self.create_source()
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def create_source(self) -> Source:
        raise NotImplementedError

    def load_bank_list(self) -> None:
        raise NotImplementedError

    # def get_pages_num_html(self, bank: BankiRuBankScheme) -> int | None:  # todo from html page?
    #     raise NotImplementedError
    #     # return int(response_json["total"]) // 24 + 1

    def send_get_request(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> requests.Response:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= {"x-requested-with": "XMLHttpRequest"}
        return super().send_get_request(url, params, header)

    def get_json_from_url(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= {"x-requested-with": "XMLHttpRequest"}
        return super().get_json_from_url(url, params, header)

    def parse(self) -> None:
        raise NotImplementedError
