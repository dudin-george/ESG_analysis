import re

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query import bank as query
from app.query.bank import create_broker_type


class BrokerParser(BaseParser):
    URL = "https://www.cbr.ru/vfs/finmarkets/files/supervision/list_brokers.xlsx"

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create_bank_type(self) -> BankType:
        return await create_broker_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse broker list")
        cbr_brokers = []
        for index, row in df.iterrows():
            license_id = int(re.sub("-", "", row["№ лицензии"]))
            name = row["Наименование организации"]
            cbr_brokers.append(Bank(licence=str(license_id), bank_name=name, bank_type_id=self.bank_type.id))
        return cbr_brokers

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        df = self.get_dataframe(self.URL)
        if df is None:
            self.logger.error("cbr.ru 403 error")
            raise Exception("cbr.ru 403 error")
        banks = self.get_bank_list(df)
        await query.load_banks(self.db, banks)
