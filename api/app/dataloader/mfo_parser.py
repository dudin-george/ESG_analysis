import asyncio
from math import ceil
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query import bank as query
from app.query.bank import create_mfo_type
from app.utils import get_json_request


class MFOParser(BaseParser):
    URL = "https://www.banki.ru/microloans/ajax/search/?catalog_name=main&period_unit=4&region_ids[]=433&region_ids[]=432&page=%i&per_page=48&total=206&page_type=MAINPRODUCT_SEARCH&sponsor_package_id=4"

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create_bank_type(self) -> BankType:
        return await create_mfo_type(self.db)

    def get_bank_list(self, items: list[dict[str, Any]]) -> list[Bank]:  # type: ignore[override]
        self.logger.info("start parse broker list")
        unique_mfos = list({(company["mfo"]["name"], company["mfo"]["ogrn"]) for company in items})
        return [Bank(id=int(ogrn), bank_name=name, bank_type_id=self.bank_type.id) for name, ogrn in unique_mfos]

    async def get_banki_mfo(self, page: int = 1) -> dict[str, Any] | None:
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "x-requested-with": "XMLHttpRequest",
        }
        url = self.URL % page
        response = await get_json_request(url, headers=header)
        if response:
            return response
        return None

    def get_total_pages(self, response: dict[str, Any]) -> int:
        page_elem = response["pagination"]
        per_page = page_elem["per_page"]
        total = page_elem["total"]
        return ceil(total / per_page)

    async def get_mfo_json(self, page: int = 1) -> dict[str, Any]:
        response = await self.get_banki_mfo(page)
        if response is None:
            self.logger.error("banki.ru 403 error")
            raise Exception("banki.ru 403 error")
        return response  # type: ignore

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        microfin: list[dict[str, Any]] = []
        first_page = await self.get_mfo_json()
        total_pages = self.get_total_pages(first_page)
        results = await asyncio.gather(*[self.get_mfo_json(i) for i in range(2, total_pages + 1)])
        microfin.extend(first_page["data"])
        for arr in results:
            microfin.extend(arr['data'])
        banks = self.get_bank_list(microfin)
        await query.load_banks(self.db, banks)
