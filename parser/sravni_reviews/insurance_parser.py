import re
from typing import Any

from common import api
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuItem


class SravniInsuranceReviews(BaseSravniReviews):
    site: str = "sravni.ru/insurance"
    organization_type = "insuranceCompany"

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        sravni_insurance_full = self.request_bank_list()
        if sravni_insurance_full is None:
            return None
        sravni_insurance = sravni_insurance_full["items"]
        self.logger.info("finish download bank list")
        existing_insurance = api.get_insurance_list()
        sravni_bank_list = []
        # todo refactor
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

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        return f"https://www.sravni.ru/strakhovaja-kompanija/{bank_info.alias}/otzyvy/{review['id']}"
