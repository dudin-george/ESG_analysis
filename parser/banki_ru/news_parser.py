import json
import re
from datetime import datetime
from math import ceil
from time import sleep

from bs4 import BeautifulSoup

from banki_ru.reviews_parser import BankiReviews
from banki_ru.schemes import BankiRuBankScheme
from common import api
from common.schemes import PatchSource, Source, SourceRequest, Text, TextRequest


class BankiNews(BankiReviews):
    def __init__(self) -> None:
        sleep(2)  # if started with reviews parser, then load banks in reviews
        super().__init__()

    def create_source(self) -> Source:
        create_source = SourceRequest(site="banki.ru/news", source_type="news")
        self.logger.debug(f"Creating source {create_source}")
        return api.send_source(create_source)

    def get_pages_num(self, bank: BankiRuBankScheme) -> int | None:
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

    def bank_news_page(self, bank: BankiRuBankScheme, page: int = 1) -> BeautifulSoup | None:
        self.logger.debug(f"Getting news page {page} for {bank.bank_name}")
        url = f"https://www.banki.ru/banks/bank/{bank.bank_code}/news/?PAGEN_2={page}"
        response = self.send_get_request(url)
        try:
            page_html = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self.logger.warning(f"Can't parse news page for {bank.bank_name} {url} {e}")
            return None
        return page_html

    def get_news_links(self, bank: BankiRuBankScheme, parsed_time: datetime, page_num: int = 1) -> list[str]:
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

    def news_from_links(self, bank: BankiRuBankScheme, news_urls: list[str]) -> list[Text]:
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

    def parse(self) -> None:
        self.logger.info("start parse banki.ru news")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank_pydantic in enumerate(self.bank_list):
            bank = BankiRuBankScheme.from_orm(bank_pydantic)
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
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
                links = self.get_news_links(bank, parsed_time, i)
                news = self.news_from_links(bank, links)
                api.send_texts(
                    TextRequest(
                        items=news,
                        parsed_state=json.dumps({"bank_id": bank.bank_id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )
                if len(news) == 0:
                    break
        self.logger.info("finish parse bank reviews")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
