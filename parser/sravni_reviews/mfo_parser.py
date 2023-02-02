from typing import Any

from common import api
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuItem


class SravniMfoReviews(BaseSravniReviews):
    site: str = "sravni.ru/mfo"
    organization_type = "mfo"
    tag = "microcredits"

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        sravni_mfo_json_full = self.request_bank_list()
        if sravni_mfo_json_full is None:
            return None
        sravni_mfo_json = sravni_mfo_json_full["items"]
        self.logger.info("finish download bank list")
        existing_mfos = api.get_mfo_list()
        sravni_bank_list = []
        # todo refactor
        for sravni_mfo in sravni_mfo_json:
            bank_db = None
            for existing_mfo in existing_mfos:
                if (int(sravni_mfo["license"]) == existing_mfo.licence) or (
                    int(sravni_mfo["requisites"]["ogrn"]) == existing_mfo.ogrn
                ):
                    bank_db = existing_mfo
                    break
            if bank_db is None:
                continue

            sravni_bank_list.append(
                SravniRuItem(
                    sravni_id=sravni_mfo["id"],
                    alias=sravni_mfo["alias"],
                    bank_id=bank_db.id,
                    bank_name=sravni_mfo["name"],
                    bank_full_name=sravni_mfo["fullName"],
                    bank_official_name=sravni_mfo["genitiveName"],
                )
            )
        banks_db = [SravniBankInfo.from_pydantic(bank) for bank in sravni_bank_list]
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        return f"https://www.sravni.ru/zaimy/{bank_info.alias}/otzyvy/{review['id']}"
