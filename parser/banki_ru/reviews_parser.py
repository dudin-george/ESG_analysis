import json
from datetime import datetime

from banki_ru.banki_base_parser import BankiBase
from banki_ru.database import BankiRuBank
from banki_ru.queries import create_banks
from banki_ru.schemes import BankiRuBankScheme, BankTypes
from common import api
from common.schemes import PatchSource, Text, TextRequest, SourceTypes


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
                    id=bank_db.id,
                    bank_id=bank_db.licence,
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
                bank_id=bank.id,
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

    def parse(self) -> None:
        self.logger.info(f"start parse banki.ru {self.source_type} {self.bank_site}")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank in enumerate(self.bank_list):
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.id < parsed_bank_id:
                continue
            start = 1
            if bank.id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = self.get_pages_num(bank)
            if total_page is None:
                continue
            for i in range(start, total_page + 1):
                self.logger.info(f"[{i}/{total_page}] start parse {bank.bank_name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time)
                if reviews_list is None:
                    break
                if len(reviews_list) == 0:
                    break

                api.send_texts(
                    TextRequest(
                        items=reviews_list,
                        parsed_state=json.dumps({"bank_id": bank.id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )

        self.logger.info(f"finish parse {self.source_type} {self.bank_site}")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
