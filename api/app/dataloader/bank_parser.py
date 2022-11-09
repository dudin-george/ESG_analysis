import re

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank
from app.dataloader.base_parser import BaseParser
from app.query.bank import create_bank_type


class CBRParser(BaseParser):
    URL = "https://www.cbr.ru/banking_sector/credit/FullCoList/"

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create_bank(self):
        return await create_bank_type(self.db)

    def get_bank_list(self, page: BeautifulSoup) -> list[Bank]:
        self.logger.info("start parse bank list")
        cbr_banks = []
        for bank in page.find_all("tr")[1:]:
            items = bank.find_all("td")
            license_id_text = items[2].text
            name = re.sub("[\xa0\n\t]", " ", items[4].text)  # todo move to validator
            if license_id_text.isnumeric():
                license_id = int(license_id_text)
            else:
                license_id = int(license_id_text.split("-")[0])  # if license id with *-K, *-M, remove suffix
            cbr_banks.append(Bank(id=license_id, bank_name=name, bank_type_id=self.bank_type.id))
        return cbr_banks
