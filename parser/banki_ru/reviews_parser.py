import json
from datetime import datetime

from banki_ru.banki_base_parser import BankiBase
from banki_ru.database import BankiRuBank
from banki_ru.queries import create_banks
from banki_ru.schemes import BankiRuBankScheme
from common import api
from common.schemes import PatchSource, Source, SourceRequest, Text, TextRequest


class BankiReviews(BankiBase):
    def __init__(self) -> None:
        super().__init__()

    def create_source(self) -> Source:
        create_source = SourceRequest(site="banki.ru", source_type="reviews")
        self.logger.debug(f"Creating source {create_source}")
        return api.send_source(create_source)

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        existing_banks = api.get_bank_list()
        banks_id = [bank.licence for bank in existing_banks]
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
            if license_id not in banks_id:
                continue

            banks.append(
                BankiRuBankScheme(
                    bank_id=license_id,
                    bank_name=bank["name"],
                    bank_code=bank["code"],
                )
            )
        self.logger.info("finish download bank list")
        banks_db = [BankiRuBank.from_pydantic(bank) for bank in banks]
        create_banks(banks_db)

    def get_page_bank_reviews(self, bank: BankiRuBankScheme, page_num: int, parsed_time: datetime) -> list[Text] | None:
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

    def get_pages_num(self, bank: BankiRuBankScheme) -> int | None:
        params = {"page": 1, "bank": bank.bank_code}
        response_json = self.get_json_from_url("https://www.banki.ru/services/responses/list/ajax/", params=params)
        if response_json is None:
            return None
        return int(response_json["total"]) // 24 + 1

    def parse(self) -> None:
        self.logger.info("start parse banki.ru reviews")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank_pydantic in enumerate(self.bank_list):
            bank = BankiRuBankScheme.from_orm(bank_pydantic)
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 1
            if bank.bank_id == parsed_bank_id:
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
                        parsed_state=json.dumps({"bank_id": bank.bank_id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )

        self.logger.info("finish parse bank reviews")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
