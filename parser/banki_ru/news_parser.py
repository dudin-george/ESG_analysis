import json
import re
from datetime import datetime
from math import ceil
from time import sleep

from bs4 import BeautifulSoup

from banki_ru.database import BankiRuBank
from banki_ru.reviews_parser import BankiReviews
from banki_ru.schemes import BankiRuBankScheme, BankTypes
from common import api
from common.schemes import PatchSource, Text, TextRequest, SourceTypes


class BankiNews(BankiReviews):
    bank_site = BankTypes.news
    source_type = SourceTypes.news

    def __init__(self) -> None:
        sleep(2)  # if started with reviews parser, then load banks in reviews
        super().__init__()

    def get_pages_num(self, bank: BankiRuBank) -> int | None:
        page = self.bank_news_page(bank)
        if page is None:
            return None
        paginator = page.find("div", {"data-module": "ui.pagination"})
        if paginator is None:
            return None
        page_params = paginator["data-options"]  # type: ignore
        params = {}
        for item in page_params.split(";"):  # type: ignore
            key, value = item.split(":")
            params[key.strip()] = value.strip()
        return ceil(int(params["totalItems"]) / int(params["itemsPerPage"]))

    def bank_news_page(self, bank: BankiRuBank, page: int = 1) -> BeautifulSoup | None:
        self.logger.debug(f"Getting news page {page} for {bank.bank_name}")
        url = f"https://www.banki.ru/banks/bank/{bank.bank_code}/news/?PAGEN_2={page}"
        response = self.send_get_request(url)
        try:
            page_html = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self.logger.warning(f"Can't parse news page for {bank.bank_name} {url} {e}")
            return None
        return page_html

    def get_news_links(self, bank: BankiRuBank, parsed_time: datetime, page_num: int = 1) -> list[str]:
        page = self.bank_news_page(bank, page_num)
        if page is None:
            return []
        news_dates = page.find_all("div", class_="widget__date")
        news_blocks = page.find_all("ul", class_="text-list text-list--date")
        news_links = []
        for date, block in zip(news_dates, news_blocks):
            parsed_date = datetime.strptime(date.text, "%d.%m.%Y")
            if parsed_date.date() < parsed_time.date():
                break
            news_times = block.find_all("span", class_="text-list-date")
            news_items = block.find_all("a", class_="text-list-link")
            for news_time, news in zip(news_times, news_items):
                time = datetime.strptime(news_time.text, "%H:%M")
                if datetime.combine(parsed_date.date(), time.time()) < parsed_time:
                    break
                url = news["href"]
                if url.startswith("/"):
                    news_links.append("https://www.banki.ru" + news["href"])
                else:
                    self.logger.warning(f"News link {url} is not valid bank {bank.bank_name} {page_num=}")
        return news_links

    def news_from_links(self, bank: BankiRuBank, news_urls: list[str]) -> list[Text]:
        texts = []
        for num_news, url in enumerate(news_urls):
            self.logger.debug(f"[{num_news+1}/{len(news_urls)}] Getting news for {bank.bank_name} from {url}")
            response = self.send_get_request(url)
            try:
                page = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                self.logger.warning(f"{e} on {url}")
                continue
            title = page.find("h1", class_="text-header-0")
            date_text = page.find("span", class_="l51e0a7a5")
            news_text_element = page.find("div", {"itemprop": "articleBody"})
            if title == "" or title is None or date_text == "" or date_text is None or news_text_element is None:
                self.logger.warning(f"Can't parse news from {url} real url {response.url}")
                continue
            paragraphs = [elem.text for elem in news_text_element.find_all("p")]  # type: ignore
            news_text = " ".join(paragraphs)
            date = re.sub(r"[\n\t]", "", date_text.text)  # todo validator
            parsed_date = datetime.strptime(date, "%d.%m.%Y %H:%M")
            texts.append(
                Text(
                    link=url,
                    date=parsed_date,
                    title=title.text,
                    text=news_text,
                    source_id=self.source.id,
                    bank_id=bank.bank_id,
                )
            )
        return texts

    def get_page_bank_reviews(self, bank: BankiRuBank, page_num: int, parsed_time: datetime) -> list[Text]:
        links = self.get_news_links(bank, parsed_time, page_num)
        news = self.news_from_links(bank, links)
        return news
