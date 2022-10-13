import json
from datetime import datetime

from bs4.element import ResultSet

from banki_ru_reviews.database import BankiRu
from banki_ru_reviews.queries import create_banks, get_bank_list
from banki_ru_reviews.shemes import BankiRuItem
from common import api
from common.base_parser import BaseParser
from common.shemes import PatchSource, SourceRequest, Text, TextRequest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from utils import get_browser, path_params_to_url
from selenium import webdriver
from typing import Any
from selenium.webdriver.common.by import By
from time import sleep


# noinspection PyMethodMayBeStatic
class BankiReviews(BaseParser):
    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        source_create = SourceRequest(site="banki.ru", source_type="reviews")
        self.source = api.send_source(source_create)
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        browser = get_browser()
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        browser.get("https://www.banki.ru/widget/ajax/bank_list.json")
        response_json = self.get_json_from_page_source(browser)
        if response_json is None:
            return None
        banks_json = response_json["data"]
        browser.close()
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
                    bank_code=bank["code"],
                )
            )
        self.logger.info("finish download bank list")
        banks_db = []
        for bank in banks:
            banks_db.append(BankiRu.from_pydantic(bank))
        create_banks(banks_db)

    def get_reviews_from_page(
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

    def get_page_bank_reviews(self, bank: BankiRuItem, page_num: int, parsed_time: datetime, browser: webdriver.Firefox | webdriver.Remote) -> list[Text] | None:
        params = {"page": page_num, "bank": bank.bank_code}
        browser.get(f"https://www.banki.ru/services/responses/list/ajax/{path_params_to_url(params)}")
        resp_json = self.get_json_from_page_source(browser)
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

    def get_json_from_page_source(self, browser: webdriver.Firefox | webdriver.Remote) -> dict[str, Any] | None:
        delay = 10
        sleep(1)
        try:
            raw_data_button = WebDriverWait(browser, delay).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="rawdata-tab"]')))
            raw_data_button.click()
            response_json = json.loads(browser.find_element(By.CLASS_NAME, "data").text)
        except json.JSONDecodeError as e:
            self.logger.warning("error parse json", e)
            return None
        return response_json

    def get_page_num(self, bank: BankiRuItem, browser: webdriver.Firefox | webdriver.Remote) -> int | None:
        params = {"page": 1, "bank": bank.bank_code}
        browser.get(f"https://www.banki.ru/services/responses/list/ajax/{path_params_to_url(params)}")
        response_json = self.get_json_from_page_source(browser)
        if response_json is None:
            return None
        return int(response_json["total"]) // 24 + 1

    def parse(self) -> None:
        self.logger.info("start parse banki.ru reviews")
        start_time = datetime.now()
        browser = get_browser()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank_pydantic in enumerate(self.bank_list):
            bank = BankiRuItem.from_orm(bank_pydantic)
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 1
            if bank.bank_id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = self.get_page_num(bank, browser)
            if total_page is None:
                continue
            for i in range(start, total_page + 1):
                self.logger.info(f"[{i}/{total_page}] start parse {bank.bank_name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time, browser)
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
        browser.close()
