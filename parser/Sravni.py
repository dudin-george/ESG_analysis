from time import sleep
from typing import List

import requests
from sqlmodel import Session, select
from tqdm import tqdm  # type: ignore

from model.Database import Database
from model.Reviews import Reviews
from model.Sourse import Source
from model.SravniBankInfo import SravniBankInfo


class Sravni:
    database: Database = Database()
    engine = database.get_engine()
    bank_list: List[SravniBankInfo] = []
    BASE_URL: str = "sravni.ru"

    def __init__(self):
        with Session(self.database.get_engine()) as session:
            self.bank_list = session.exec(select(SravniBankInfo)).all()
            if len(self.bank_list) == 0:
                self.get_bank_list()
            self.source = session.exec(
                select(Source).where(Source.site == self.BASE_URL)
            ).one()

    def get_bank_list(self) -> None:
        print("get")
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
        print("load get")
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
            self.bank_list = session.exec(select(SravniBankInfo)).all()

    def parse(self) -> None:
        for bank_info in tqdm(self.bank_list):
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
                    session.add_all(reviews)
                    session.commit()
                break
            sleep(1)
        return
