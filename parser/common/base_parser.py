import json
from datetime import datetime
from time import sleep
from typing import Any

import requests
from fake_useragent import UserAgent
from requests import Response
from requests.exceptions import ConnectTimeout, JSONDecodeError, SSLError

from common.settings import get_settings
from common.shemes import Source
from utils.logger import get_logger


class BaseParser:
    settings = get_settings()
    logger = get_logger(__name__, settings.logger_level)

    def parse(self) -> None:
        raise NotImplementedError

    def get_source_params(self, source: Source) -> tuple[int, int, datetime]:
        parsed_time = source.last_update
        if parsed_time is None:
            parsed_time = datetime.fromtimestamp(1)
        parsed_state = {}
        if source.parser_state is not None:
            parsed_state = json.loads(source.parser_state)
        parsed_bank_id = int(parsed_state.get("bank_id", "0"))
        parsed_bank_page = int(parsed_state.get("page_num", "0"))
        return parsed_bank_page, parsed_bank_id, parsed_time

    def send_get_request(self, url: str, params: dict[str, Any] = {}) -> requests.Response:
        ua = UserAgent()
        response = Response()
        log_params = params.copy()
        if "access_token" in log_params.keys():
            log_params["access_token"] = "..."
        for _ in range(5):
            headers = {"User-Agent": ua.random}
            try:
                self.logger.debug(f"send request to {url} with {log_params=}")
                response = requests.get(url, headers=headers, params=params)
            except (SSLError, ConnectTimeout) as error:
                self.logger.warning(f"{type(error)} when request {response.url} {error=}")
                sleep(30)
            except Exception as error:
                self.logger.warning(f"{type(error)} when request {response.url} {error=}")
                sleep(30)
            if response.status_code == 200:
                break
        return response

    def get_json(self, response: Response) -> dict[str, Any] | None:
        if response.status_code != 200:
            self.logger.warning(response.json())
            return None
        try:
            json_response = response.json()  # type: dict[str, Any]
        except JSONDecodeError as error:
            self.logger.warning(f"Bad json on {response.url} {error=}")
            return None
        except Exception as error:
            self.logger.warning(f"Bad json on {response.url} {error=}")
            return None
        if "error" in json_response.keys():
            self.logger.warning(f"Error in json {json_response}")
            sleep(5)
            return None
        return json_response
