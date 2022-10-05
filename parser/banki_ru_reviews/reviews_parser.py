import json
import re
from datetime import datetime
from math import ceil

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from selenium import webdriver

from banki_ru_reviews.database import BankiRu
from banki_ru_reviews.queries import create_banks, get_bank_list
from banki_ru_reviews.shemes import BankiRuItem
from utils import api, get_browser
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

    def get_page_num(self, page: BeautifulSoup, per_page: int = 50) -> int:
        page_num_text = page.find("div", class_="ui-pagination__description")
        if page_num_text is None:
            return -1
        page_num = ceil(int(page_num_text.text.strip().split()[-1]) / per_page)
        return page_num

    def get_page(self, browser: webdriver.Firefox | webdriver.Remote, url: str) -> BeautifulSoup:
        browser.get(url)
        self.logger.debug(f"Send request to {url}")
        page = BeautifulSoup(browser.page_source, "html.parser")
        return page

    def get_bank(self, page: BeautifulSoup) -> BankiRuItem | None:
        bank_link = page.find("a", class_="widget__link")
        bank_address = page.find("div", {"data-test": "banks-item-address"})
        if bank_link is None or bank_address is None:
            return None
        license_text = bank_address.find_all("span")[-1].text  # type: ignore
        if license_text.find("№") == -1:
            return None
        license_id_text = license_text.split("№")[-1].split()[0]
        if license_id_text.isnumeric():
            license_id = int(license_id_text)
        else:
            license_id = int(license_id_text.split("-")[0])
        bank_url = bank_link["href"].replace("/banks/", "https://www.banki.ru/services/responses/")  # type: ignore
        return BankiRuItem(bank_id=license_id, bank_name=bank_link.text, reviews_url=bank_url)

    def get_bank_list(self) -> None:
        browser = get_browser()
        self.logger.info("start download bank list")
        page = self.get_page(browser, "https://www.banki.ru/banks/")
        page_num = self.get_page_num(page)
        banks = []
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        for i in range(1, page_num + 1):
            if i != 1:
                page = self.get_page(browser, f"https://www.banki.ru/banks/?PAGEN_1={i}")
            for bank_page_item in page.find_all("tr", {"data-test": "banks-list-item"}):
                bank = self.get_bank(bank_page_item)
                if bank is None or bank.bank_id not in banks_id:
                    continue
                banks.append(bank)
        self.logger.info("finish download bank list")
        banks_db = []
        for bank in banks:
            banks_db.append(BankiRu.from_pydantic(bank))
        create_banks(banks_db)
        browser.quit()

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
                    text=re.sub("[\xa0\n\t]", " ", text),  # TODO validator
                    comments_num=comments_num,
                    bank_id=bank_id,
                    source_id=self.source.id,
                )
            )
            times.append(time)
        return reviews_list, times

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
        parsed_bank_id = parsed_state.get("bank_id", "0")
        browser = get_browser()
        for bank_index, bank_pydantic in enumerate(self.bank_list):
            bank = BankiRuItem.from_orm(bank_pydantic)
            if bank.bank_id <= parsed_bank_id:
                continue
            reviews_list = []
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            page = self.get_page(browser, bank.reviews_url)
            page_num = self.get_page_num(page, 25)
            if page_num == -1:
                continue

            for i in range(1, page_num + 1):
                self.logger.info(f"[{i}/{page_num}] start parse {bank.bank_name} reviews page {i}")
                if i != 1:
                    page = self.get_page(browser, f"{bank.reviews_url}?page={i}")

                responses_list = page.find("div", class_="responses-list")
                if responses_list is None:
                    continue
                response_array = responses_list.find_all("article")  # type: ignore
                responses, times = self.get_reviews(response_array, parsed_time, bank.bank_id)

                if len(times) == 0:
                    break

                if max(times) < parsed_time:
                    break

                reviews_list.extend(responses)

            api.send_texts(
                TextRequest(
                    items=reviews_list, parsed_state=json.dumps({"bank_id": bank.bank_id}), last_update=parsed_time
                )
            )

        browser.quit()
        self.logger.info("finish parse bank reviews")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
