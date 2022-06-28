import datetime
from time import sleep
from typing import List

import requests
from sqlmodel import Session, select
from tqdm import tqdm  # type: ignore

from model.Database import Database
from model.Reviews import Reviews
from model.Sourse import Source
from model.SravniBankInfo import SravniBankInfo
from misc import Logger
from datetime import datetime


class SravniReviews:
    logger = Logger.get_logger(__name__)
    database = Database()
    engine = database.get_engine()
    bank_list: List[SravniBankInfo] = []
    BASE_URL: str = "sravni.ru"

    def __init__(self) -> None:
        with Session(self.database.get_engine()) as session:
            self.bank_list = session.exec(select(SravniBankInfo)).all()
            if len(self.bank_list) == 0:
                self.get_bank_list()
            self.source = session.exec(select(Source).where(Source.site == self.BASE_URL)).one()

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

        bank_list = []
        for item in r.json()["items"]:
            bank_list.append(
                SravniBankInfo(
                    id=item["_id"],
                    bank_name=item["name"]["accusative"],
                    alias=item["alias"],
                )
            )

        with Session(self.engine) as session:
            session.add_all(bank_list)
            session.commit()
            self.logger.info("commit banks to db")
            self.bank_list = session.exec(select(SravniBankInfo)).all()

    def parse(self) -> None:
        last_date = self.source.last_checked if self.source.last_checked is not None else datetime.min

        for bank_info in tqdm(self.bank_list):
            self.logger.info(f"download reviews for {bank_info.bank_name}")
            reviews = requests.get(
                "https://www.sravni.ru/proxy-reviews/reviews?locationRoute=&newIds=true&orderBy=withRates&pageIndex"
                f"=0&pageSize=100000&rated=any&reviewObjectId={bank_info.id}&reviewObjectType=bank&tag"
            ).json()
            if "items" in reviews.keys():
                reviews_array = reviews["items"]
                reviews = []
                for review in reviews_array:
                    url = f"https://www.sravni.ru/bank/{bank_info.alias}/otzyvy/{review['id']}"
                    reviews.append(
                        Reviews(
                            source=self.source.id,
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
