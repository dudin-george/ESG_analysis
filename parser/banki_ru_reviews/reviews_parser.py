import json
from datetime import datetime
from time import sleep
from typing import Any

import requests
from bs4.element import ResultSet
from fake_useragent import UserAgent
from requests import Response
from requests.exceptions import JSONDecodeError, SSLError, ConnectTimeout

from banki_ru_reviews.database import BankiRu
from banki_ru_reviews.queries import create_banks, get_bank_list
from banki_ru_reviews.shemes import BankiRuItem
from utils import api
from utils.base_parser import BaseParser
from utils.logger import get_logger
from utils.settings import Settings
from utils.shemes import PatchSource, SourceRequest, Text, TextRequest


# noinspection PyMethodMayBeStatic
class BankiReviews(BaseParser):
    logger = get_logger(__name__, Settings().logger_level)

    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        source_create = SourceRequest(site="banki.ru", source_type="reviews")
        self.source = api.send_source(source_create)
        if len(self.bank_list) == 0:
            self.get_bank_list()
            self.bank_list = get_bank_list()

    # noinspection PyDefaultArgument
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

    def get_bank_list(self) -> None:
        self.logger.info("start download bank list")
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        response = self.send_get_request("https://www.banki.ru/widget/ajax/bank_list.json")
        banks_json = response.json()["data"]
        banks = []
        for bank in banks_json:
            if bank["licence"] == "—" or bank["licence"] == "" or bank["licence"] == "-":
                continue
            license_id_str = bank["licence"].split("-")[0]
            if license_id_str.isnumeric():
                license_id = int(license_id_str)
            else:
                license_id = int(license_id_str.split()[0])
            if license_id not in banks_id:
                continue

            banks.append(
                BankiRuItem(
                    bank_id=license_id,
                    bank_name=bank["name"],
                    bank_code=bank['code'],
                )
            )
        self.logger.info("finish download bank list")
        banks_db = []
        for bank in banks:
            banks_db.append(BankiRu.from_pydantic(bank))
        create_banks(banks_db)

    def get_reviews(
        self, reviews: ResultSet, parsed_time: datetime, bank_id: int  # type: ignore
    ) -> tuple[list[Text], list[datetime]]:
        reviews_list = []
        times = []
        for review in reviews:
            header = review.find("a", {"class": "header-h3"})
            link = "https://www.banki.ru" + header["href"]
            title = header.text
            text = review.find("div", class_="markup-inside-small").text
            time = datetime.strptime(
                review.find("time", class_="display-inline-block").text,
                "%d.%m.%Y %H:%M",
            )
            comments_num_elem = review.find("span", class_="responses__item__comment-count")
            comments_num = int(comments_num_elem.text) if comments_num_elem is not None else 0
            if time < parsed_time:
                continue

            reviews_list.append(
                Text(
                    link=link,
                    date=time,
                    title=title,
                    text=text,
                    comments_num=comments_num,
                    bank_id=bank_id,
                    source_id=self.source.id,
                )
            )
            times.append(time)
        return reviews_list, times

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

    def get_page_bank_reviews(self, bank: BankiRuItem, page_num: int, parsed_time: datetime) -> list[Text] | None:
        params = {"page": page_num, "bank": bank.bank_code}
        response = self.send_get_request("https://www.banki.ru/services/responses/list/ajax/", params)
        if response.status_code != 200:
            return None
        resp_json = self.get_json(response)
        if resp_json is None:
            return None
        texts = []
        for item in resp_json["data"]:
            text = Text(
                link=f"https://www.banki.ru/services/responses/bank/response/{item['id']}",
                date=item["dateCreate"],
                title=item["title"],
                text=item["text"],
                comments_num=item["commentCount"],
                source_id=self.source.id,
                bank_id=bank.bank_id,
            )
            if text.date < parsed_time:
                continue
            texts.append(text)
        return texts

    def get_page_num(self, bank: BankiRuItem) -> int | None:
        params = {"page": 1, "bank": bank.bank_code}
        response = self.send_get_request("https://www.banki.ru/services/responses/list/ajax/", params)
        if response.status_code != 200:
            return None
        response_json = self.get_json(response)
        if response_json is None:
            return None
        return int(response_json["total"]) // 24 + 1

    def parse(self) -> None:
        self.logger.info("start parse banki.ru reviews")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_time = current_source.last_update
        if parsed_time is None:
            parsed_time = datetime.min
        parsed_state = {}
        if current_source.parser_state is not None:
            parsed_state = json.loads(current_source.parser_state)
        parsed_bank_id = int(parsed_state.get("bank_id", "0"))
        parsed_bank_page = int(parsed_state.get("page_num", "0"))
        for bank_index, bank_pydantic in enumerate(self.bank_list):
            bank = BankiRuItem.from_orm(bank_pydantic)
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 1
            if bank.bank_id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = None
            for _ in range(5):
                total_page = self.get_page_num(bank)
                if total_page is not None:
                    break
            if total_page is None:
                continue
            for i in range(start, total_page+1):
                self.logger.info(f"[{i}/{total_page}] start parse {bank.bank_name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time)
                if reviews_list is None:
                    break
                if len(reviews_list) == 0:
                    break

                api.send_texts(
                    TextRequest(
                        items=reviews_list,
                        parsed_state=json.dumps({"bank_id": bank.bank_id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )

        self.logger.info("finish parse bank reviews")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
