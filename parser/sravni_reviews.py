from datetime import datetime
from time import sleep
from typing import List

import requests
from sqlmodel import Session, select

from misc import Logger
from model.banks import Banks
from model.database import Database
from model.reviews import Reviews
from model.sourse import Source
from model.sravni_bank_info import SravniBankInfo


class SravniReviews:
    logger = Logger.get_logger(__name__)
    database = Database()
    engine = database.get_engine()
    bank_list: List[SravniBankInfo] = []
    BASE_URL: str = "sravni.ru reviews"
    source: Source

    def __init__(self) -> None:
        with Session(self.database.get_engine()) as session:
            self.bank_list = session.exec(select(SravniBankInfo)).all()
            if len(self.bank_list) == 0:
                self.get_bank_list()

    def get_bank_list(self) -> None:
        self.logger.info("start download bank list")
        self.logger.info("send request to https://www.sravni.ru/proxy-organizations/banks/list")
        r = requests.post(
            "https://www.sravni.ru/proxy-organizations/banks/list",
            data={
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
            },
        )
        self.logger.info("finish download bank list")

        sravni_bank_list = []
        bank_list = []
        for item in r.json()["items"]:
            names = item["name"]
            bank = Banks(bank_name=names["short"], bank_full_name=names["full"], bank_official_name=names["official"])
            bank_list.append(bank)
            sravni_bank_list.append(
                SravniBankInfo(sravni_id=item["_id"], sravni_old_id=item["oldId"], alias=item["alias"], bank_id=bank.id)
            )

        with Session(self.engine) as session:
            session.add_all(bank_list)
            session.commit()
            self.logger.info("create main table for banks")

            for i in range(len(bank_list)):
                sravni_bank_list[i].bank_id = bank_list[i].id  # type: ignore
            session.add_all(sravni_bank_list)
            session.commit()
            self.logger.info("commit banks to db")
            self.bank_list = session.exec(select(SravniBankInfo)).all()

    def parse(self) -> None:
        with Session(self.database.get_engine()) as session:
            self.source = session.exec(select(Source).where(Source.name == self.BASE_URL)).one()
        last_date = self.source.last_checked if self.source.last_checked is not None else datetime.min

        for i, bank_info in enumerate(self.bank_list):
            self.logger.info(f"[{i}/{len(self.bank_list)}] download reviews for {bank_info.alias}")
            reviews = requests.get(
                "https://www.sravni.ru/proxy-reviews/reviews?locationRoute=&newIds=true&orderBy=withRates&pageIndex"
                f"=0&pageSize=100000&rated=any&reviewObjectId={bank_info.sravni_id}&reviewObjectType=bank&tag"
            ).json()
            if "items" in reviews.keys():
                reviews_array = reviews["items"]
                reviews = []
                for review in reviews_array:
                    url = f"https://www.sravni.ru/bank/{bank_info.alias}/otzyvy/{review['id']}"
                    reviews.append(
                        Reviews(
                            source_id=self.source.id,
                            bank_id=bank_info.bank_id,
                            link=url,
                            date=review["date"],
                            title=review["title"],
                            text=review["text"],
                            rating=review["rating"],
                            comments_num=review["commentsCount"],
                            user_id=review["userId"],
                        )
                    )

                with Session(self.engine) as session:
                    for review in reviews:
                        last_date = max(review.date.replace(tzinfo=None), last_date)
                        if self.source.last_checked is None:
                            session.add(review)
                        elif self.source.last_checked < review.date.replace(tzinfo=None):
                            session.add(review)
                    self.logger.info("commit reviews to db")
                    session.commit()
            sleep(1)

        with Session(self.engine) as session:
            if self.source.last_checked is None:
                self.source.last_checked = last_date
                session.add(self.source)
            if last_date > self.source.last_checked:
                self.source.last_checked = last_date
                session.add(self.source)
            session.commit()
