from datetime import datetime
from typing import Any

from banki_ru.banki_base_parser import BankiBase
from banki_ru.database import BankiRuBase, BankiRuMfo
from banki_ru.queries import create_banks
from banki_ru.schemes import BankiRuBankScheme, BankTypes
from common import api
from common.schemes import SourceTypes, Text


class BankiMfo(BankiBase):
    bank_site = BankTypes.mfo
    source_type = SourceTypes.reviews
    url = "https://www.banki.ru/microloans/responses/ajax/responses/"
    per_page = 200
    params = {"perPage": per_page, "grade": "all", "status": "all"}

    def get_mfo_json(self, page: int = 1) -> dict[str, Any] | None:
        params = {
            "catalog_name": "main",
            "period_unit": 4,
            "region_ids[]": ["433", "432"],
            "page": page,
            "per_page": 48,
            "total": 206,
            "page_type": "MAINPRODUCT_SEARCH",
            "sponsor_package_id": "4",
        }
        return self.get_json_from_url("https://www.banki.ru/microloans/ajax/search/", params=params)

    def get_mfo_json_reviews(self, bank: BankiRuBase, page: int = 1) -> dict[str, Any] | None:
        params = self.params.copy()
        params["companyCodes"] = bank.bank_code
        params["page"] = page
        return self.get_json_from_url(self.url, params=params)

    def json_total_pages(self, response: dict[str, Any]) -> int:
        page_elem = response["pagination"]
        per_page = int(page_elem["per_page"])
        total = int(page_elem["total"])
        return total // per_page + 1

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        existing_mfos = api.get_mfo_list()
        microfin = []
        first_page = self.get_mfo_json()
        if first_page is None:
            return None
        total_pages = self.json_total_pages(first_page)
        results = [self.get_mfo_json(i) for i in range(2, total_pages + 1)]
        microfin.extend(first_page["data"])
        for arr in results:
            if arr is None:
                continue
            microfin.extend(arr["data"])
        unique_mfos = list(
            {(company["mfo"]["name"], int(company["mfo"]["ogrn"]), company["mfo"]["code"]) for company in microfin}
        )
        return_microfin = []
        for name, ogrn, code in unique_mfos:
            bank_db = None
            for existing_bank in existing_mfos:  # todo to different func
                if existing_bank.licence == ogrn:  # todo change to license (certificate)
                    bank_db = existing_bank
                    break
            if bank_db is None:
                continue

            return_microfin.append(
                BankiRuBankScheme(
                    bank_id=bank_db.id,
                    bank_name=name,
                    bank_code=code,
                )
            )
        self.logger.info("finish download mfo list")
        banks_db: list[BankiRuBase] = [BankiRuMfo.from_pydantic(bank) for bank in return_microfin]
        create_banks(banks_db)

    def get_page_bank_reviews(self, bank: BankiRuBase, page_num: int, parsed_time: datetime) -> list[Text] | None:
        reviews_json = self.get_mfo_json_reviews(bank, page_num)
        reviews = []
        for review in reviews_json["responses"]["data"]:  # type: ignore[index]
            text = Text(
                title=review["title"],
                text=review["text"],
                link=f"https://www.banki.ru/microloans/responses/response/{review['id']}/",
                date=review["createdAt"],
                source_id=self.source.id,
                bank_id=bank.bank_id,
                comments_num=review["commentsCount"],
            )
            if text.date.replace(tzinfo=None) < parsed_time:
                continue
            reviews.append(text)
        return reviews

    def get_pages_num(self, bank: BankiRuBase) -> int | None:
        response_json = self.get_mfo_json_reviews(bank)
        if response_json is None:
            return None
        return int(response_json["responses"]["total"]) // self.per_page + 1
