import json
import re
from datetime import datetime
from time import sleep

from banki_ru.banki_base_parser import BankiBase
from banki_ru.database import BankiRuInsurance
from banki_ru.queries import create_banks
from banki_ru.schemes import BankTypes
from common import api
from common.schemes import SourceTypes, Text, TextRequest, PatchSource


class BankiInsurance(BankiBase):
    bank_site = BankTypes.insurance
    source_type = SourceTypes.reviews
    url = "https://www.banki.ru/insurance/responses/company/"

    def __init__(self) -> None:
        sleep(2)
        super().__init__()

    def load_bank_list(self) -> None:
        insurances = []
        existing_insurances = api.get_insurance_list()
        insurances_id = [bank.licence for bank in existing_insurances]
        url = "https://www.banki.ru/insurance/companies/"
        total_pages = self.get_pages_num_html(url)
        for pages in range(1, total_pages):
            soup = self.get_page_from_url(url, params={"page": pages})
            for row in soup.find_all("tr", {"data-test": "list-row"}):
                bank_text_url = row.find("a", class_="widget__link")  # todo to validator
                license_text = row.find(
                    "div",
                    class_="inline-elements inline-elements--x-small font-size-small color-gray-blue margin-top-xx-small"
                )
                license_arr = re.findall("(?<=№\\s)\\d+(?=\\s)", license_text.text)
                insurance_license = None
                if len(license_arr) == 1:
                    insurance_license = int(license_arr[0])
                if insurance_license not in insurances_id:
                    continue
                insurances.append(
                    BankiRuInsurance(bank_id=insurance_license, bank_name=bank_text_url.text, bank_url=bank_text_url['href'])
                )
        self.logger.info("finish download bank list")
        # banks_db = [BankiRuBank.from_pydantic(bank) for bank in banks]
        create_banks(insurances)

    def get_pages_num(self, bank: BankiRuInsurance) -> int | None:
        url = f"{self.url}{bank.bank_code}"
        return self.get_pages_num_html(url)

    def get_page_bank_reviews(self, bank: BankiRuInsurance, page_num: int, parsed_time: datetime) -> list[Text] | None:
        url = f"{self.url}{bank.bank_code}"
        soup = self.get_page_from_url(url, params={"page": page_num, "isMobile": 0})
        if soup is None:
            return None
        texts = []
        for review in soup.find_all("div", {"data-test": "responses__item"}):
            title_elem = review.find("div", {"data-test": "responses-header"})
            title = title_elem.text
            link = "https://www.banki.ru"+title_elem["href"]
            text = review.find("div", {"class": "responses__item__message markup-inside-small markup-inside-small--bullet", "data-full": ""}).text.strip()
            date_elem = review.find("time")
            comment_count = review.find("span", class_="responses__item__comments-count")
            text = Text(
                date=date_elem["datetime"],
                title=title,
                text=text,
                link=link,
                comment_count=comment_count.text,
                source_id=self.source.id,
                bank_id=bank.bank_id,
            )
            if text.date < parsed_time:
                continue
            texts.append(text)
        return texts

    def parse(self) -> None:  # todo try to base class
        self.logger.info("start parse banki.ru insurance reviews")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank in enumerate(self.bank_list):
            self.logger.info(f"[{bank_index + 1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 1
            if bank.bank_id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = self.get_pages_num(bank)
            if total_page is None:
                continue
            for i in range(start, total_page + 1):
                self.logger.info(f"[{i}/{total_page}] start parse {bank.bank_name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time)
                if reviews_list is None:
                    break
                if len(reviews_list) == 0:
                    break

                api.send_texts(
                    TextRequest(
                        items=reviews_list,
                        parsed_state=json.dumps({"bank_id": bank.bank_id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )

        self.logger.info("finish parse bank reviews")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
