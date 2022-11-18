import json

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query import bank as query
from app.query.bank import create_mfo_type


class MFOParser(BaseParser):
    URL = "https://www.cbr.ru/vfs/finmarkets/files/supervision/list_MFO.xlsx"

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create_bank_type(self) -> BankType:
        return await create_mfo_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse broker list")
        cbr_brokers = []
        df["Регистрационный номер записи"] = df["Регистрационный номер записи"].fillna(0)
        df["licence"] = (
                df["Unnamed: 5"]
                + df["Unnamed: 4"] * 1e6
                + df["Unnamed: 3"] * 1e8
                + df["Unnamed: 2"] * 1e11
                + df["Регистрационный номер записи"] * 1e12
        )
        df["licence"] = df["licence"].astype(int)
        for index, row in df.iterrows():
            name = row["Полное наименование"]
            cbr_brokers.append(
                Bank(
                    licence=str(row["licence"]),
                    bank_name=name,
                    bank_type_id=self.bank_type.id,
                    description=json.dumps(
                        {
                            "ogrn": row["Основной государственный регистрационный номер"],
                            "short_name": row["Сокращенное наименование"],  # short name have one NaN
                        }
                    ),
                )
            )
        return cbr_brokers

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        df = self.get_dataframe(self.URL, skip_rows=4, index_col=0)
        if df is None:
            self.logger.error("cbr.ru 403 error")
            raise Exception("cbr.ru 403 error")
        banks = self.get_bank_list(df)
        await query.load_banks(self.db, banks)
