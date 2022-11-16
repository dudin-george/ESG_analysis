import re
from typing import Any

import requests

from banki_ru.queries import get_bank_list
from banki_ru.schemes import BankTypes
from common import api
from common.base_parser import BaseParser
from common.schemes import Source, SourceRequest, SourceTypes
from bs4 import BeautifulSoup


class BankiBase(BaseParser):
    headers = {
        "X-Requested-With": "XMLHttpRequest"
    }
    bank_site: BankTypes
    source_type: SourceTypes

    def __init__(self) -> None:
        self.bank_list = get_bank_list(self.bank_site)
        self.source = self.create_source()
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list(self.bank_site)

    def create_source(self) -> Source:
        create_source = SourceRequest(site=self.bank_site, source_type=self.source_type)
        self.logger.debug(f"Creating source {create_source}")
        return api.send_source(create_source)

    def load_bank_list(self) -> None:
        raise NotImplementedError

    def get_pages_num_html(self, url: str) -> int | None:  # todo from html page?
        response = self.send_get_request(url)
        if response.status_code != 200:
            return None
        page = BeautifulSoup(response.text, "html.parser")
        items_num_text = page.find("span", class_="ui-pagination__description")
        if items_num_text is None:
            return 1
        items_num = [int(num) for num in re.findall("\\d+", items_num_text.text)]
        # items num text pattern 1-10 из 100 -> [1, 10, 100] -> 100 / (10 - 1)
        return items_num[2] // (items_num[1] - items_num[0] + 1) + 1

    def send_get_request(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> requests.Response:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= self.headers
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

    def get_page_from_url(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> BeautifulSoup | None:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= self.headers
        return super().get_page_from_url(url, params, header)
