from datetime import datetime

from banki_ru.banki_base_parser import BankiBase
from banki_ru.database import BankiRuBank
from banki_ru.queries import create_banks
from banki_ru.schemes import BankiRuBankScheme, BankTypes
from common import api
from common.schemes import SourceTypes, Text


class BankiReviews(BankiBase):
    bank_site = BankTypes.bank
    source_type = SourceTypes.reviews

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        existing_banks = api.get_bank_list()
        response_json = self.get_json_from_url("https://www.banki.ru/widget/ajax/bank_list.json")
        if response_json is None:
            return None
        banks_json = response_json["data"]
        banks = []
        for bank in banks_json:  # todo validator
            if bank["licence"] == "—" or bank["licence"] == "" or bank["licence"] == "-":
                continue
            license_id_str = bank["licence"].split("-")[0]
            if license_id_str.isnumeric():
                license_id = int(license_id_str)
            else:
                license_id = int(license_id_str.split()[0])
            bank_db = None
            for existing_bank in existing_banks:
                if existing_bank.licence == license_id:
                    bank_db = existing_bank
                    break
            if bank_db is None:
                continue

            banks.append(
                BankiRuBankScheme(
                    bank_id=bank_db.id,
                    bank_name=bank["name"],
                    bank_code=bank["code"],
                )
            )
        self.logger.info("finish download bank list")
        banks_db = [BankiRuBank.from_pydantic(bank) for bank in banks]
        create_banks(banks_db)

    def get_page_bank_reviews(self, bank: BankiRuBank, page_num: int, parsed_time: datetime) -> list[Text] | None:
        params = {"page": page_num, "bank": bank.bank_code}
        response_json = self.get_json_from_url("https://www.banki.ru/services/responses/list/ajax/", params=params)
        if response_json is None:
            return None
        texts = []
        for item in response_json["data"]:
            text = Text(
                link=f"https://www.banki.ru/services/responses/bank/response/{item['id']}",
                date=item["dateCreate"],
                title=item["title"],
                text=item["text"],
                comments_num=item["commentCount"],
                source_id=self.source.id,
                bank_id=bank.bank_id,
            )
            if text.date < parsed_time:
                continue
            texts.append(text)
        return texts

    def get_pages_num(self, bank: BankiRuBank) -> int | None:
        params = {"page": 1, "bank": bank.bank_code}
        response_json = self.get_json_from_url("https://www.banki.ru/services/responses/list/ajax/", params=params)
        if response_json is None:
            return None
        return int(response_json["total"]) // 25 + 1
