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

    def get_pages_num_insurance_list(self, url: str) -> int:
        page = self.get_page_from_url(url)
        total_page_elem = page.find("div", {"data-module": "ui.pagination"})  # currentPageNumber: 1; itemsPerPage: 15; totalItems: 157; title: Страховых компаний
        total_page = int(re.findall("(?<=totalItems:\\s)\\d+(?=;)", total_page_elem["data-options"])[0])
        per_page = int(re.findall("(?<=itemsPerPage:\\s)\\d+(?=;)", total_page_elem["data-options"])[0])
        return total_page // per_page + 1

    def load_bank_list(self) -> None:
        insurances = []
        existing_insurances = api.get_insurance_list()
        url = "https://www.banki.ru/insurance/companies/"
        total_pages = self.get_pages_num_insurance_list(url)
        for pages in range(1, total_pages + 1):
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
                bank_db = None
                for bank in existing_insurances:
                    if bank.licence == insurance_license:
                        bank_db = bank
                        break
                if bank_db is None:
                    continue
                insurances.append(
                    BankiRuInsurance(
                        bank_id=bank_db.id, bank_name=bank_text_url.text, bank_code=bank_text_url["href"].split("/")[-2]
                    )
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
        for review in soup.find_all("article"):
            title_elem = review.find("a", class_="header-h3")
            title = title_elem.text
            link = "https://www.banki.ru"+title_elem["href"]
            text = review.find("div", {"class": "responses__item__message markup-inside-small markup-inside-small--bullet", "data-full": ""}).text.strip()
            date_elem = review.find("time", {"data-test": "responses-datetime", "pubdate": ""})
            comment_count = review.find("span", class_="responses__item__comment-count")
            text = Text(
                date=date_elem["datetime"],
                title=title,
                text=text,
                link=link,
                comment_count=comment_count.text if comment_count else None,
                source_id=self.source.id,
                bank_id=bank.bank_id,
            )
            if text.date < parsed_time:
                continue
            texts.append(text)
        return texts
