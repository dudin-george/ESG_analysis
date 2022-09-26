import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from db.banks import Banks
from db.database import engine
from db.reviews import Reviews
from db.sites_banks import SravniBankInfo
from db.sourse import Source
from sqlmodel import Session, select


class SravniNews:
    BASE_URL: str = "sravni.ru reviews"

    def __init__(self) -> None:
        with Session(engine) as session:
            bank_list = session.exec(select(SravniBankInfo)).all()
            if len(bank_list) == 0:
                # self.get_bank_list()
                pass

    def parse(self) -> None:
        with Session(engine) as session:
            source = session.exec(
                select(Source).where(Source.name == self.BASE_URL)
            ).one()
            bank_list = session.exec(select(SravniBankInfo)).all()
        for bank in bank_list:
            id = bank.sravni_old_id
            urls = []
            for page in range(5):
                r = requests.post(
                    "https://www.sravni.ru/ajax/partnernews/",
                    data={"page": page, "organizationId": id},
                )
                for news in r.json():
                    urls.append(news["url"])

            # for i, url in enumerate(urls):
            #     self.logger.info(f"[{i}/{len(bank_list)}] download reviews for {bank.alias}")
            #     r = requests.get("https://www.sravni.ru" + url)
            #     page = BeautifulSoup(r.text, "html.parser")
            #     if page.find("script", {"id": "__NEXT_DATA__"}) is not None:
            #         data = json.loads(page.find("script", {"id": "__NEXT_DATA__"}).text)["props"]["initialReduxState"]["news"]["material"]["data"]
            #         if len(data) == 0:
            #             continue
            #         news = data[0]
            #         Reviews(link=url, source=source, date=datetime.strptime(news["publishDate"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            #                 title=,
            #                 text=BeautifulSoup(news["htmlBody"]).text,
            #                 rating=news["likes"], )
            #         name = news["organizationData"]["name"]
            #         news["htmlHead"] = None
            #         news["picture"] = None
            #         news["miniPicture"] = None
            #         news["htmlBody"] =
            #         news_list.append({"name": name} | news)
