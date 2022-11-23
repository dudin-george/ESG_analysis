import json
from datetime import datetime
from typing import Any

from common import api
from common.schemes import Text
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuItem


# noinspection PyMethodMayBeStatic
class SravniMfoReviews(BaseSravniReviews):
    site: str = "sravni.ru/mfo"

    def request_bank_list(self) -> dict[str, Any]:
        page = self.get_page_from_url("https://www.sravni.ru/zaimy/mfo/")
        return json.loads(page.find(id="__NEXT_DATA__").text)

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        sravni_mfo_json_full = self.request_bank_list()
        sravni_mfo_json = sravni_mfo_json_full["props"]["initialReduxState"]["organizations"]["list"]
        self.logger.info("finish download bank list")
        existing_mfos = api.get_mfo_list()
        sravni_bank_list = []

        for sravni_mfo in sravni_mfo_json:
            bank_db = None
            for existing_mfo in existing_mfos:
                description = json.loads(existing_mfo["description"])
                if (int(sravni_mfo["license"]) == int(existing_mfo["licence"])) or (int(sravni_mfo['orgn']) == int(description['ogrn'])):
                    bank_db = existing_mfo
                    break
            if bank_db is None:
                continue

            sravni_bank_list.append(
                SravniRuItem(
                    sravni_id=sravni_mfo["id"],
                    alias=sravni_mfo["alias"],
                    bank_id=bank_db.id,
                    bank_name=sravni_mfo["name"]["short"],
                    bank_full_name=sravni_mfo["name"]["full"],
                    bank_official_name=sravni_mfo["name"]["official"],
                )
            )
        banks_db = [SravniBankInfo.from_pydantic(bank) for bank in sravni_bank_list]
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def load_mfo_reviews(self, bank_info: SravniBankInfo, page: int = 0) -> dict[str, Any]:
        url = "https://www.sravni.ru/proxy-reviews/reviews"
        params = {
            "filterBy": "withRates",
            "fingerPrint": "9be16a8e68e64e948f4465306f63c9ec",
            "isClient": False,
            "locationRoute": "",
            "newIds": True,
            "orderBy": "byDate",
            "pageIndex": page,
            "pageSize": 1000,
            "reviewObjectId": bank_info.sravni_id,
            "reviewObjectType": "mfo",
            "specificProductId": "",
            "tag": "microcredits",
            "withVotes": True,
        }
        return self.get_json_from_url(url, params=params)

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        reviews_json = self.load_mfo_reviews(bank_info)
        total_pages = int(reviews_json["total"]) // 1000 + 1
        reviews = []
        for page in range(total_pages):
            if page != 0:
                reviews_json = self.load_mfo_reviews(bank_info, page)
            reviews_list = reviews_json["items"]
            for review in reviews_list:
                text = Text(
                    bank_id=bank_info.bank_id,
                    title=review["title"],
                    text=review["text"],
                    date=review["createdToMoscow"],
                    source=self.source.id,
                    link=f"https://www.sravni.ru/zaimy/{bank_info.alias}/otzyvy/{review['id']}",
                )
                if text.date < parsed_time:
                    break
                reviews.append(text)
        return reviews
