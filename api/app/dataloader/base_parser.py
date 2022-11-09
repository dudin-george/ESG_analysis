import requests
from bs4 import BeautifulSoup
from fastapi.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.query import bank as query


class BaseParser:
    logger = logger
    bank_type: BankType = None
    URL = ""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def load_banks(self) -> None:
        self.bank_type = await self.create_bank()
        count = await query.get_bank_count(self.db)
        if count == 0:
            await self.parse()
        self.logger.info(f"finish download {self.bank_type.name} list")

    async def create_bank(self) -> BankType:
        raise NotImplementedError

    def get_page(self, url: str) -> BeautifulSoup | None:
        response = requests.get(url)
        if response.status_code == 403:
            self.logger.error("cbr.ru 403 error")
            return None
        page = BeautifulSoup(response.text, "html.parser")
        return page

    def get_bank_list(self, page: BeautifulSoup) -> list[Bank]:
        raise NotImplementedError

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        page = self.get_page(self.URL)
        if page is None:
            self.logger.error("cbr.ru 403 error")
            raise Exception("cbr.ru 403 error")
        banks = self.get_bank_list(page)
        await query.load_banks(self.db, banks)
