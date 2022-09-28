from datetime import datetime
from queue import api
from queue.sravni_ru import create_banks, get_bank_list

import requests
from requests import Response

from database.reviews_site import SravniBankInfo
from misc.logger import get_logger
from shemes.bank import Source, SravniRuItem, Text, TextRequest


class SravniReviews:
    logger = get_logger(__name__)
    source = Source(site="sravni.ru", source_type="reviews")

    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        self.source_id = api.send_source(self.source)
        if len(self.bank_list) == 0:
            self.get_bank_list()

    def request_bank_list(self) -> dict:
        data = {
            "select": [
                "oldId",
                "alias",
                "name",
                "license",
                "status",
                "ratings",
                "contacts",
                "requisites",
            ],
            "statuses": "active",
            "type": "bank",
            "limit": 1000,
            "skip": 0,
            "sort": ["-ratings", "ratings.assetsRatingPosition"],
            "location": "6.",
            "isMainList": True,
        }
        return requests.post("https://www.sravni.ru/proxy-organizations/banks/list", data=data).json()["items"]

    def get_bank_list(self) -> None:
        self.logger.info("start download bank list")
        self.logger.info("send request to https://www.sravni.ru/proxy-organizations/banks/list")
        items = self.request_bank_list()
        self.logger.info("finish download bank list")
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        sravni_bank_list = []
        for item in items:
            if item["license"] not in banks_id:
                continue
            names = item["name"]
            sravni_bank_list.append(
                SravniRuItem(
                    sravni_id=item["_id"],
                    sravni_old_id=item["oldId"],
                    alias=item["alias"],
                    bank_id=item["license"],
                    bank_name=names["short"],
                    bank_full_name=names["full"],
                    bank_official_name=names["official"],
                )
            )
        banks_db = []
        for bank in sravni_bank_list:
            banks_db.append(SravniBankInfo.from_pydantic(bank))
        create_banks(banks_db)
        self.bank_list = banks_db
        self.logger.info("create main table for banks")

    def parse_reviews(self, reviews_array: dict, last_date: datetime, bank: SravniBankInfo) -> list[Text]:
        reviews = []
        for review in reviews_array:
            url = f"https://www.sravni.ru/bank/{bank.alias}/otzyvy/{review['id']}"
            parsed_review = Text(
                source_id=self.source_id,
                bank_id=bank.bank_id,
                link=url,
                date=review["date"],
                title=review["title"],
                text=review["text"],
                comments_num=review["commentsCount"],
            )
            if last_date > parsed_review.date.replace(tzinfo=None):
                continue
            reviews.append(parsed_review)
        return reviews

    def get_bank_info(self, bank_info: SravniBankInfo) -> Response:
        response = Response()
        for _ in range(3):
            response = requests.get(
                "https://www.sravni.ru/proxy-reviews/reviews?locationRoute=&newIds=true&orderBy=withRates&pageIndex"
                f"=0&pageSize=100000&rated=any&reviewObjectId={bank_info.sravni_id}&reviewObjectType=bank&tag"
            )
            if response.status_code != 500:
                return response.json()
        return response

    def parse(self) -> None:
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source_id)
        parsed_time = current_source.last_update
        if parsed_time is None:
            parsed_time = datetime.min

        for i, bank_info in enumerate(self.bank_list):
            self.logger.info(f"[{i}/{len(self.bank_list)}] download reviews for {bank_info.alias}")
            response = self.get_bank_info(bank_info)

            if response.status_code == 500 or response.status_code is None:
                continue
            reviews_json = response.json()
            if "items" in reviews_json.keys():
                reviews_array = reviews_json["items"]
                reviews = self.parse_reviews(reviews_array, parsed_time, bank_info)
                api.send_texts(TextRequest(items=reviews, last_update=start_time))
                self.logger.info("commit reviews to db")
