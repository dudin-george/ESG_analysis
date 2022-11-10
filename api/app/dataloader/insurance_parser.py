import re

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query import bank as query
from app.query.bank import create_insurance_type


class InsuranceParser(BaseParser):
    URL = "https://www.cbr.ru/vfs/finmarkets/files/supervision/list_ssd.xlsx"

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create_bank_type(self) -> BankType:
        return await create_insurance_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse broker list")
        cbr_brokers = []
        df = df[["Наименование субъекта страхового дела", "Лицензия"]].dropna()
        df["Лицензия"] = [int(re.findall(r"\d+", s)[0]) for s in df["Лицензия"].values]
        for index, row in df.iterrows():
            license_id = row["Лицензия"]
            name = row["Наименование субъекта страхового дела"]
            cbr_brokers.append(Bank(id=license_id, bank_name=name, bank_type_id=self.bank_type.id))
        return cbr_brokers

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        df = self.get_dataframe(self.URL, skip_rows=2)
        if df is None:
            self.logger.error("cbr.ru 403 error")
            raise Exception("cbr.ru 403 error")
        banks = self.get_bank_list(df)
        await query.load_banks(self.db, banks)
