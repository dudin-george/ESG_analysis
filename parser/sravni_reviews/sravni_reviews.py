from datetime import datetime
from math import ceil

import requests
from requests import Response

from common import api
from common.schemes import Text
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuItem


# noinspection PyMethodMayBeStatic
class SravniReviews(BaseSravniReviews):
    site: str = "sravni.ru"

    def request_bank_list(self) -> Response:
        params = {"active": True, "limit": 400, "organizationType": "bank", "skip": 0} # todo request json
        return requests.get("https://www.sravni.ru/proxy-organizations/organizations", params=params)  # type: ignore

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        self.logger.info("send request to https://www.sravni.ru/proxy-organizations/organizations")
        request = self.request_bank_list()
        items = request.json()["items"]
        self.logger.info("finish download bank list")
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        sravni_bank_list = []
        for item in items:
            license_id_str = item["license"].split("-")[0]
            license_id = int(license_id_str)
            if license_id not in banks_id:
                continue

            sravni_bank_list.append(
                SravniRuItem(
                    sravni_id=item["_id"],
                    sravni_old_id=item["oldId"],
                    alias=item["alias"],
                    bank_id=license_id,
                    bank_name=item["name"],
                    bank_full_name=item["prepositionalName"],
                    bank_official_name=item["fullName"],
                )
            )
        banks_db = []
        for bank in sravni_bank_list:
            banks_db.append(SravniBankInfo.from_pydantic(bank))
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def parse_reviews(
        self, reviews_array: list[dict[str, str]], last_date: datetime, bank: SravniBankInfo
    ) -> list[Text]:
        reviews = []
        for review in reviews_array:
            url = f"https://www.sravni.ru/bank/{bank.alias}/otzyvy/{review['id']}"
            # noinspection PyTypeChecker
            parsed_review = Text(
                source_id=self.source.id,
                bank_id=bank.bank_id,
                link=url,
                date=review["date"],
                title=review["title"],
                text=review["text"],
                comments_num=int(review["commentsCount"]),
            )
            if last_date > parsed_review.date.replace(tzinfo=None):
                continue
            reviews.append(parsed_review)
        return reviews

    def get_bank_reviews(self, bank_info: SravniBankInfo, page_num: int = 0, page_size: int = 1000) -> Response:
        params = {
            "filterBy": "withRates",
            "isClient": False,
            "locationRoute": None,
            "newIds": True,
            "orderBy": "byDate",
            "pageIndex": page_num,
            "pageSize": page_size,
            "reviewObjectId": bank_info.sravni_id,
            "reviewObjectType": "bank",
            "specificProductId": None,
            "tag": None,
            "withVotes": True,
        }
        response = self.send_get_request("https://www.sravni.ru/proxy-reviews/reviews/", params=params)
        if response.status_code != 200:
            self.logger.warning(f"error {response.status_code} for {bank_info.alias}")
        return response

    def get_num_reviews(self, bank_info: SravniBankInfo) -> int:
        response = self.get_bank_reviews(bank_info, page_size=1)
        if response.status_code != 200:
            self.logger.warning(f"error {response.status_code} for {bank_info.alias} url {response.url}")
            return 0
        reviews_total = int(response.json()["total"])
        return ceil(reviews_total / 1000)

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        reviews_array = []
        page_num = self.get_num_reviews(bank_info)
        for i in range(page_num):
            self.logger.debug(f"[{i + 1}/{page_num}] download page {i + 1} for {bank_info.alias}")
            response = self.get_bank_reviews(bank_info, i)

            if response.status_code == 500 or response.status_code is None:
                break
            reviews_json = self.get_json(response)
            if reviews_json is None:
                break
            reviews_json_items = reviews_json.get("items", [])
            if len(reviews_json_items) == 0:
                break
            parsed_reviews = self.parse_reviews(reviews_json_items, parsed_time, bank_info)
            reviews_array.extend(parsed_reviews)
            times = [review.date for review in parsed_reviews]
            if len(times) == 0 or min(times).replace(tzinfo=None) <= parsed_time:
                break
        return reviews_array
