from typing import Any
import requests
from requests.exceptions import JSONDecodeError, SSLError, ConnectTimeout
from fake_useragent import UserAgent
from time import sleep
from requests import Response

from common.settings import Settings
from utils.logger import get_logger


class BaseParser:
    logger = get_logger(__name__, Settings().logger_level)

    def parse(self) -> None:
        pass

    def send_get_request(self, url: str, params: dict[str, Any] = {}) -> requests.Response:
        ua = UserAgent()
        response = Response()
        for _ in range(5):
            headers = {"User-Agent": ua.random}
            try:
                self.logger.debug(f"send request to {url} with {params=}")
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
        try:
            resp_json = response.json()  # type: dict[str, Any]
        except JSONDecodeError as error:
            self.logger.warning(f"Bad json on {response.url} {error=}")
            return None
        except Exception as error:
            self.logger.warning(f"Bad json on {response.url} {error=}")
            return None
        return resp_json
