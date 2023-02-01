import json
from datetime import datetime
from math import ceil
from typing import Any

from common import api
from common.base_parser import BaseParser
from common.requests_ import get_json_from_url
from common.schemes import PatchSource, SourceRequest, Text, TextRequest
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import get_bank_list


# noinspection PyMethodMayBeStatic
class BaseSravniReviews(BaseParser):
    site: str
    organization_type: str
    tag: str | None = None

    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        source_create = SourceRequest(site=self.site, source_type="reviews")
        self.source = api.send_source(source_create)
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def request_bank_list(self) -> dict[str, Any] | None:
        params = {"active": True, "limit": 400, "organizationType": self.organization_type, "skip": 0}
        return get_json_from_url("https://www.sravni.ru/proxy-organizations/organizations", params=params)

    def get_bank_reviews(
        self, bank_info: SravniBankInfo, page_num: int = 0, page_size: int = 1000
    ) -> dict[str, Any] | None:
        params = {
            "filterBy": "withRates",
            "isClient": False,
            "locationRoute": None,
            "newIds": True,
            "orderBy": "byDate",
            "pageIndex": page_num,
            "pageSize": page_size,
            "reviewObjectId": bank_info.sravni_id,
            "reviewObjectType": self.organization_type,
            "specificProductId": None,
            "tag": self.tag,
            "withVotes": True,
        }
        json_response = get_json_from_url("https://www.sravni.ru/proxy-reviews/reviews", params=params)
        if not json_response:
            self.logger.warning(f"error for {bank_info.alias}")
        return json_response

    def get_num_reviews(self, bank_info: SravniBankInfo) -> int:
        json_response = self.get_bank_reviews(bank_info, page_size=1)
        if json_response is None:
            return 0
        reviews_total = int(json_response["total"])
        return ceil(reviews_total / 1000)

    def load_bank_list(self) -> None:
        raise NotImplementedError

    # todo combine from classes
    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        raise NotImplementedError

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        raise NotImplementedError

    def parse(self) -> None:
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        _, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for i, bank_info in enumerate(self.bank_list):
            self.logger.info(f"[{i + 1}/{len(self.bank_list)}] download reviews for {bank_info.alias}")
            if bank_info.bank_id <= parsed_bank_id:
                continue
            reviews = self.get_reviews(parsed_time, bank_info)
            time = datetime.now()
            api.send_texts(
                TextRequest(
                    items=reviews, parsed_state=json.dumps({"bank_id": bank_info.bank_id}), last_update=parsed_time
                )
            )
            self.logger.debug(f"Time for {bank_info.alias} send reviews: {datetime.now() - time}")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
