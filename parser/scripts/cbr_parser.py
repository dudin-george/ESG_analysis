import re

import requests
from bs4 import BeautifulSoup
from db.banks import Banks
from db.database import engine
from misc.logger import get_logger
from sqlmodel import Session, select


class CBRParser:
    logger = get_logger(__name__)

    def __init__(self) -> None:
        pass

    def parse(self) -> None:
        with Session(engine) as session:
            bank_list = session.exec(select(Banks)).all()
            if len(bank_list) != 0:
                return
        self.logger.info("start download bank list")
        response = requests.get("https://www.cbr.ru/banking_sector/credit/FullCoList/")
        if response.status_code == 403:
            self.logger.error("cbr.ru 403 error")
            return
        page = BeautifulSoup(response.text, "html.parser")

        cbr_banks = []
        for bank in page.find_all("tr")[1:]:
            items = bank.find_all("td")
            license_id = items[2].text
            name = re.sub("[\xa0\n\t]", "", items[4].text.strip())
            license_status = items[7].text.strip()
            cbr_banks.append(
                Banks(id=license_id, bank_name=name, bank_status=license_status)
            )

        with Session(engine) as session:
            session.add_all(cbr_banks)
            session.commit()
        self.logger.info("finish download bank list")
