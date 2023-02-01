import re
from datetime import datetime
from typing import Any

from common import api
from common.requests_ import get_json_from_url
from common.schemes import Text
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuItem


class SravniInsuranceReviews(BaseSravniReviews):
    site: str = "sravni.ru/insurance"

    def request_bank_list(self) -> dict[str, Any]:
        params = {"active": True, "limit": 200, "organizationType": "insuranceCompany", "skip": 0}
        return get_json_from_url("https://www.sravni.ru/proxy-organizations/organizations", params=params)  # type: ignore

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        sravni_insurance = self.request_bank_list()["items"]
        self.logger.info("finish download bank list")
        existing_insurance = api.get_insurance_list()
        sravni_bank_list = []
        for insurance in sravni_insurance:
            if len(insurance["license"]) == 0:
                continue
            sravni_license = int(re.findall(r"(?:(?<=№)|(?<=№\s))\d+(?:(?=\sот)|(?=-\d+|\s))", insurance["license"])[0])
            bank_db = None
            for existing_bank in existing_insurance:
                if existing_bank.licence == sravni_license:
                    bank_db = existing_bank
                    break
            if bank_db is None:
                continue

            sravni_bank_list.append(
                SravniRuItem(
                    sravni_id=insurance["id"],
                    alias=insurance["alias"],
                    bank_id=bank_db.id,
                    bank_name=insurance["name"],
                    bank_full_name=insurance["prepositionalName"],
                    bank_official_name=insurance["fullName"],
                )
            )
        banks_db = [SravniBankInfo.from_pydantic(bank) for bank in sravni_bank_list]
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def load_bank_reviews(self, bank_info: SravniBankInfo, page: int = 0) -> dict[str, Any]:
        url = "https://www.sravni.ru/proxy-reviews/reviews"
        params = {
            "filterBy": "withRates",
            "isClient": False,
            "locationRoute": "",
            "newIds": True,
            "orderBy": "byDate",
            "pageIndex": page,
            "pageSize": 1000,
            "reviewObjectId": bank_info.sravni_id,
            "reviewObjectType": "insuranceCompany",
            "specificProductId": "",
            "tag": "",
            "withVotes": True,
        }
        return get_json_from_url(url, params=params)  # type: ignore

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        reviews_json = self.load_bank_reviews(bank_info)
        total_pages = int(reviews_json["total"]) // 1000 + 1
        reviews = []
        for page in range(total_pages):
            if page != 0:
                reviews_json = self.load_bank_reviews(bank_info, page)
            reviews_list = reviews_json["items"]
            for review in reviews_list:
                text = Text(
                    bank_id=bank_info.bank_id,
                    title=review["title"],
                    text=review["text"],
                    date=review["createdToMoscow"],
                    source_id=self.source.id,
                    link=f"https://www.sravni.ru/strakhovaja-kompanija/{bank_info.alias}/otzyvy/{review['id']}",
                )
                if text.date < parsed_time:
                    break
                reviews.append(text)
        return reviews
