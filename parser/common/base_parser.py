import json
from abc import ABC
from datetime import datetime
from time import sleep
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import ConnectTimeout, JSONDecodeError, SSLError

from common.schemes import Source
from common.settings import get_settings
from utils.logger import get_logger


class BaseParser(ABC):
    settings = get_settings()
    logger = get_logger(__name__, settings.logger_level)

    def parse(self) -> None:
        raise NotImplementedError

    def get_source_params(self, source: Source) -> tuple[int, int, datetime]:
        self.logger.debug(f"get source params {source=}")
        parsed_time = source.last_update
        if parsed_time is None:
            parsed_time = datetime.fromtimestamp(1)
        parsed_time = parsed_time.replace(tzinfo=None)
        parsed_state = {}
        if source.parser_state is not None:
            parsed_state = json.loads(source.parser_state)
        parsed_bank_id = int(parsed_state.get("bank_id", "0"))
        parsed_bank_page = int(parsed_state.get("page_num", "0"))
        return parsed_bank_page, parsed_bank_id, parsed_time

    def send_get_request(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> requests.Response:
        if params is None:
            params = {}
        if header is None:
            header = {}
        response = Response()
        log_params = params.copy()
        if "access_token" in log_params.keys():
            log_params["access_token"] = "..."
        for _ in range(5):
            header |= {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
            try:
                self.logger.debug(f"send request to {url} with {log_params=}")
                response = requests.get(url, headers=header, params=params)
            except (SSLError, ConnectTimeout) as error:
                self.logger.warning(f"{type(error)} when request {response.url} {error=}")
                sleep(30)
            except Exception as error:
                self.logger.warning(f"{type(error)} when request {response.url} {error=}")
                sleep(30)
            if response.status_code == 200:
                break
            sleep(2)
        return response

    def get_json(self, response: Response) -> dict[str, Any] | None:
        if response.status_code != 200:
            self.logger.warning(f"response status code is {response.status_code}")
            self.logger.warning(response.text)
            return None
        try:
            json_response = response.json()  # type: dict[str, Any]
        except JSONDecodeError as error:
            self.logger.warning(f"Bad json on {response.url} {error=} {response.text=}")
            return None
        except Exception as error:
            self.logger.warning(f"Bad json on {response.url} {error=} {response.text=}")
            return None
        if "error" in json_response.keys() and json_response["error"] is not None:
            self.logger.warning(f"Error in json {json_response} Error: {response.json()['error']}")
            sleep(5)
            return None
        return json_response

    def get_json_from_url(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        response = self.send_get_request(url, params, header)
        return self.get_json(response)

    def get_page_from_url(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> BeautifulSoup | None:
        response = self.send_get_request(url, params, header)
        page = BeautifulSoup(response.text, "html.parser")
        return page
