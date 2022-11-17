import re
from datetime import datetime

from banki_ru.banki_base_parser import BankiBase
from banki_ru.database import BankiRuBank, BankiRuBroker
from banki_ru.queries import create_banks
from banki_ru.schemes import BankiRuBankScheme, BankTypes
from common import api
from common.schemes import SourceTypes, Text


class BankiBroker(BankiBase):
    bank_site = BankTypes.broker
    source_type = SourceTypes.reviews

    def get_broker_licence_from_url(self, url: str) -> str | None:
        broker_json = self.get_json_from_url(url)
        if broker_json is None:
            return None
        broker_license_str = broker_json["data"]["broker"]["licence"]
        return broker_license_str

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        existing_brokers = api.get_broker_list()
        brokers_json = self.get_json_from_url("https://www.banki.ru/investment/brokers/list/")
        if brokers_json is None:
            return None
        brokers = []
        total_brokers = len(brokers_json["data"])
        for i, broker in enumerate(brokers_json["data"]):
            self.logger.info(f"[{i+1}/{total_brokers}] start download broker {broker['name']}")
            name_arr = broker["name"].split()
            if len(name_arr) == 0 or name_arr[0] == "Заявка":
                continue
            broker_license_unparsed = self.get_broker_licence_from_url(broker["url"])
            if broker_license_unparsed is None:
                continue
            broker_license_unparsed = re.sub("-", "", broker_license_unparsed)
            broker_license_arr = re.findall("\\d{8}100000|\\d{8}300000", broker_license_unparsed)
            broker_license = int(broker_license_arr[0])  # todo to validator
            bank_db = None
            for existing_bank in existing_brokers:  # todo to different func
                if existing_bank.licence == broker_license:
                    bank_db = existing_bank
                    break
            if bank_db is None:
                continue

            brokers.append(
                BankiRuBankScheme(
                    bank_id=bank_db.id,
                    bank_name=broker["name"],
                    bank_code=broker["url"].split("/")[-2],
                )
            )
        self.logger.info("finish download broker list")
        banks_db = [BankiRuBroker.from_pydantic(bank) for bank in brokers]
        create_banks(banks_db)

    def get_page_bank_reviews(self, bank: BankiRuBank, page_num: int, parsed_time: datetime) -> list[Text] | None:
        url = f"https://www.banki.ru/investment/responses/company/broker/{bank.bank_code}/"
        texts = self.get_reviews_from_url(url, bank, parsed_time, params={"page": page_num, "isMobile": 0})
        return texts

    def get_pages_num(self, bank: BankiRuBank) -> int | None:
        params = {"page": 1, "isMobile": 0}
        total_pages = self.get_pages_num_html(f"https://www.banki.ru/investment/responses/company/broker/{bank.bank_code}/", params=params)
        return total_pages
