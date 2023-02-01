from datetime import datetime
from typing import Any

from common import api
from common.schemes import Text
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuItem


# noinspection PyMethodMayBeStatic
class SravniReviews(BaseSravniReviews):
    site: str = "sravni.ru"
    organization_type: str = "bank"

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        self.logger.info("send request to https://www.sravni.ru/proxy-organizations/organizations")
        response_bank_list = self.request_bank_list()
        if response_bank_list is None:
            return None
        items = response_bank_list["items"]
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
        banks_db = [SravniBankInfo().from_pydantic(bank) for bank in sravni_bank_list]
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def parse_reviews(
        self, reviews_array: list[dict[str, str]], last_date: datetime, bank: SravniBankInfo
    ) -> list[Text]:
        reviews = []
        for review in reviews_array:
            parsed_review = Text(
                source_id=self.source.id,
                bank_id=bank.bank_id,
                link=self.get_review_link(bank, review),
                date=review["date"],  # todo check created to moscow time
                title=review["title"],
                text=review["text"],
                comments_num=review["commentsCount"],
            )
            if last_date > parsed_review.date.replace(tzinfo=None):
                continue
            reviews.append(parsed_review)
        return reviews

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        return f"https://www.sravni.ru/bank/{bank_info.alias}/otzyvy/{review['id']}"

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        reviews_array = []
        page_num = self.get_num_reviews(bank_info)
        for i in range(page_num):
            self.logger.debug(f"[{i + 1}/{page_num}] download page {i + 1} for {bank_info.alias}")
            reviews_json = self.get_bank_reviews(bank_info, i)
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
