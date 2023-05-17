import re

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query.bank import create_bank_type
from app.utils import send_get


class BankParser(BaseParser):
    BASE_PAGE_URL = "https://www.cbr.ru/banking_sector/credit/FullCoList/"

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.URL = self.get_dataframe_url()

    async def create_bank_type(self) -> BankType:
        return await create_bank_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse bank list")
        return [
            Bank(
                id=row["cregnum"], licence=str(row["cregnum"]), bank_name=row["csname"], bank_type_id=self.bank_type.id
                # Set id because on first implementation, when insurance and brokers weren't collected licence = id
            )
            for index, row in df.iterrows()
        ]

    def get_dataframe_url(self) -> str:
        response = send_get(self.BASE_PAGE_URL)
        if response is None or response.status_code != 200:
            raise Exception("cbr.ru 403 error")
        # Pattern to find url in html that contains link to xlsx file
        pattern = re.compile(r'<a\s+class="b-export_button"\s+title="Экспортировать в XLSX"\s+href="([^"]+)"')
        match = pattern.search(response.text)
        if match is None:
            self.logger.error("Url not found")
            raise Exception("Url not found")
        path = match.group(1).replace("&amp;", "&")
        return f"https://www.cbr.ru{path}"
