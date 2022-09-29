import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app.database.bank import Bank
from app.query.bank import get_bank_count, load_bank


class CBRParser:
    logger = logger

    def __init__(self, db: Session) -> None:
        self.db = db

    def load_banks(self) -> None:
        with self.db as session:
            count = get_bank_count(session)
        if count == 0:
            self.parse()
        self.logger.info("finish download bank list")

    def get_page(self) -> BeautifulSoup | None:
        response = requests.get("https://www.cbr.ru/banking_sector/credit/FullCoList/")
        if response.status_code == 403:
            self.logger.error("cbr.ru 403 error")
            return None
        page = BeautifulSoup(response.text, "html.parser")
        return page

    def get_bank_list(self, page: BeautifulSoup) -> list[Bank]:
        self.logger.info("start parse bank list")
        cbr_banks = []
        for bank in page.find_all("tr")[1:]:
            items = bank.find_all("td")
            license_id = items[2].text
            name = re.sub("[\xa0\n\t]", " ", items[4].text)
            cbr_banks.append(Bank(id=license_id, bank_name=name))
        return cbr_banks

    def parse(self) -> None:
        self.logger.info("start download bank list")
        page = self.get_page()
        if page is None:
            while page is None:
                page = self.get_page()
                sleep(3)
        banks = self.get_bank_list(page)
        with self.db as session:
            load_bank(session, banks)
