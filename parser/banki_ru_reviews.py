import re
from datetime import datetime
from math import ceil

from bs4 import BeautifulSoup
from sqlmodel import Session, select

from db.banks import Banks
from db.database import engine
from db.reviews import Reviews
from db.sites_banks import InfoBankiRu
from db.sourse import Source
from misc import get_browser
from misc.logger import get_logger


class BankiReviews:
    logger = get_logger(__name__)
    BASE_URL: str = "banki.ru reviews"

    def __init__(self) -> None:
        with Session(engine) as session:
            bank_list = session.exec(select(InfoBankiRu)).all()
            if len(bank_list) == 0:
                self.get_bank_list()

    def get_bank_list(self) -> None:
        browser = get_browser()
        self.logger.info("start download bank list")
        browser.get("https://www.banki.ru/banks/")
        page = BeautifulSoup(browser.page_source, "html.parser")
        page_num_text = page.find("div", class_="ui-pagination__description")
        page_num = ceil(int(page_num_text.text.strip().split()[-1]) / 50)  # type: ignore
        banks = []

        with Session(engine) as session:
            existing_id = session.exec(select(Banks.id)).all()
            cbr_banks = select(Banks)
            for i in range(1, page_num + 1):
                if i != 1:
                    self.logger.info(f"start download bank list page {i}")
                    browser.get(f"https://www.banki.ru/banks/?PAGEN_1={i}")
                page = BeautifulSoup(browser.page_source, "html.parser")
                for bank in page.find_all("tr", {"data-test": "banks-list-item"}):
                    bank_link = bank.find("a", class_="widget__link")
                    bank_adress = bank.find("div", {"data-test": "banks-item-address"})
                    license_text = bank_adress.find_all("span")[-1].text
                    license_id = None
                    id_exist = False
                    if license_text.find("№") != -1:
                        license_id = license_text.split("№")[-1].split()[0]
                        id_exist = license_id in existing_id

                    if id_exist and license_id is not None:
                        cbr_bank = session.exec(cbr_banks.where(Banks.id == license_id)).one()
                    else:
                        continue
                    bank_url = bank_link["href"].replace("/banks/", "https://www.banki.ru/services/responses/")
                    banks.append(InfoBankiRu(bank_name=bank_link.text, reviews_url=bank_url, bank=cbr_bank))
            session.add_all(banks)
            session.commit()
        browser.stop_client()
        browser.quit()
        self.logger.info("finish download bank list")

    def parse(self) -> None:
        with Session(engine) as session:
            source = session.exec(select(Source).where(Source.name == self.BASE_URL)).one()
            bank_list = session.exec(select(InfoBankiRu)).all()

            self.logger.info("start parse banki.ru reviews")
            start_time = datetime.now()

            parsed_time = source.last_checked if source.last_checked is not None else datetime.min
            browser = get_browser()
            for bank_index, bank in enumerate(bank_list):
                reviews_list = []
                self.logger.info(f"[{bank_index+1}/{len(bank_list)}] Start parse bank {bank.bank_name}")
                browser.get(bank.reviews_url)
                self.logger.debug(f"Send request to {bank.reviews_url}")
                page = BeautifulSoup(browser.page_source, "html.parser")

                reviews_num_elem_main = page.find("div", class_="ui-pagination__description")
                if reviews_num_elem_main is None:
                    continue
                reviews_num_elem = reviews_num_elem_main.find_all("span")[1]  # type: ignore
                reviews_num = reviews_num_elem.text.strip().split()[-1]
                page_num = ceil(int(reviews_num) / 25)

                for i in range(1, page_num + 1):
                    self.logger.info(f"[{i}/{page_num}] start parse {bank.bank_name} reviews page {i}")
                    if i != 1:
                        browser.get(f"{bank.reviews_url}?page={i}")
                    page = BeautifulSoup(browser.page_source, "html.parser")
                    if page.find("div", class_="responses-list") is None:
                        continue

                    times = []
                    responses_list = page.find("div", class_="responses-list")
                    responses = responses_list.find_all("article")  # type: ignore
                    for response in responses:
                        link = "https://www.banki.ru" + response.find("a", {"class": "header-h3"})["href"]
                        title = response.find("a", {"class": "header-h3"}).text
                        text = response.find("div", class_="markup-inside-small").text
                        time = datetime.strptime(
                            response.find("time", class_="display-inline-block").text, "%d.%m.%Y %H:%M"
                        )
                        comments_num = response.find("span", class_="responses__item__comment-count")
                        rating_text = response.find("span", class_="rating-grade")
                        rating = int(rating_text.text) if rating_text is not None else None

                        if time < parsed_time:
                            continue

                        reviews_list.append(
                            Reviews(
                                link=link,
                                date=time,
                                title=title,
                                text=re.sub("[\xa0\n\t]", "", text),
                                rating=rating,
                                bank=bank.bank,
                                source=source,
                                comments_num=comments_num,
                            )
                        )
                        times.append(time)

                    if len(times) == 0:
                        break

                    if max(times) < parsed_time:
                        break

                session.add_all(reviews_list)
                session.commit()

            source.last_checked = start_time
            session.add(source)
            session.commit()

        browser.stop_client()
        browser.quit()
        self.logger.info("finish parse bank reviews")
