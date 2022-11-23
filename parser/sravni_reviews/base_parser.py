import json
from datetime import datetime

from common import api
from common.base_parser import BaseParser
from common.schemes import PatchSource, SourceRequest, Text, TextRequest
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import get_bank_list


# noinspection PyMethodMayBeStatic
class BaseSravniReviews(BaseParser):
    site: str

    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        source_create = SourceRequest(site=self.site, source_type="reviews")
        self.source = api.send_source(source_create)
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def load_bank_list(self) -> None:
        raise NotImplementedError

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
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
