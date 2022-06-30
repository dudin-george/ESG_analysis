from datetime import datetime

import requests
from sqlmodel import Session, select

from misc import Logger
from model.banks import Banks
from model.database import engine
from model.reviews import Reviews
from model.sourse import Source
from model.sravni_bank_info import SravniBankInfo


class SravniReviews:
    logger = Logger.get_logger(__name__)
    BASE_URL: str = "sravni.ru reviews"

    def __init__(self) -> None:
        with Session(engine) as session:
            bank_list = session.exec(select(SravniBankInfo)).all()
            if len(bank_list) == 0:
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
                SravniBankInfo(sravni_id=item["_id"], sravni_old_id=item["oldId"], alias=item["alias"], bank=bank)
            )

        with Session(engine) as session:
            session.add_all(bank_list)
            session.add_all(sravni_bank_list)
            session.commit()
            self.logger.info("create main table for banks")

    def parse(self) -> None:
        with Session(engine) as session:
            source = session.exec(select(Source).where(Source.name == self.BASE_URL)).one()
            bank_list = session.exec(select(SravniBankInfo)).all()
            last_date = source.last_checked if source.last_checked is not None else datetime.min

            for i, bank_info in enumerate(bank_list):
                self.logger.info(f"[{i}/{len(bank_list)}] download reviews for {bank_info.alias}")
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
                                source=source,
                                bank=bank_info.bank,
                                link=url,
                                date=review["date"],
                                title=review["title"],
                                text=review["text"],
                                rating=review["rating"],
                                comments_num=review["commentsCount"],
                                user_id=review["userId"],
                            )
                        )

                    for review in reviews:
                        last_date = max(review.date.replace(tzinfo=None), last_date)
                        if source.last_checked is None:
                            session.add(review)
                        elif source.last_checked < review.date.replace(tzinfo=None):
                            session.add(review)
                    self.logger.info("commit reviews to db")
                    session.commit()

            if source.last_checked is None:
                source.last_checked = last_date
                session.add(source)
            if last_date > source.last_checked:
                source.last_checked = last_date
                session.add(source)
            session.commit()
