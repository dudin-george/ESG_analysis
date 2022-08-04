from datetime import datetime

import requests
from sqlmodel import Session, select

from db.banks import Banks
from db.database import engine
from db.reviews import Reviews
from db.sites_banks import SravniBankInfo
from db.sourse import Source
from misc.logger import get_logger


class SravniReviews:
    logger = get_logger(__name__)
    BASE_URL: str = "sravni.ru reviews"

    def __init__(self) -> None:
        with Session(engine) as session:
            bank_list = session.exec(select(SravniBankInfo)).all()
            if len(bank_list) == 0:
                self.get_bank_list()

    def get_bank_list(self) -> None:
        self.logger.info("start download bank list")
        with Session(engine) as session:
            cbr_banks = select(Banks)
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
            for item in r.json()["items"]:
                names = item["name"]
                bank = session.exec(cbr_banks.where(Banks.id == item["license"])).one()
                sravni_bank_list.append(
                    SravniBankInfo(
                        sravni_id=item["_id"],
                        sravni_old_id=item["oldId"],
                        alias=item["alias"],
                        bank=bank,
                        bank_name=names["short"],
                        bank_full_name=names["full"],
                        bank_official_name=names["official"],
                    )
                )

                session.add_all(sravni_bank_list)
                session.commit()
            self.logger.info("create main table for banks")

    def parse(self) -> None:
        start_date = datetime.now()
        with Session(engine) as session:
            source = session.exec(select(Source).where(Source.name == self.BASE_URL)).one()
            bank_list = session.exec(select(SravniBankInfo)).all()
            # last_date = source.last_checked if source.last_checked is not None else datetime.min
            last_date = datetime(2022, 1, 1)
            for i, bank_info in enumerate(bank_list):
                self.logger.info(f"[{i}/{len(bank_list)}] download reviews for {bank_info.alias}")
                for _ in range(3):
                    response = requests.get(
                        "https://www.sravni.ru/proxy-reviews/reviews?locationRoute=&newIds=true&orderBy=withRates&pageIndex"
                        f"=0&pageSize=100000&rated=any&reviewObjectId={bank_info.sravni_id}&reviewObjectType=bank&tag"
                    )
                    if response.status_code != 500:
                        break
                if response.status_code == 500:
                    continue
                reviews_json = response.json()
                if "items" in reviews_json.keys():
                    reviews_array = reviews_json["items"]
                    reviews = []
                    for review in reviews_array:
                        url = f"https://www.sravni.ru/bank/{bank_info.alias}/otzyvy/{review['id']}"
                        parsed_review = Reviews(
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
                        if last_date > parsed_review.date.replace(tzinfo=None):
                            continue
                        reviews.append(parsed_review)

                    session.add_all(reviews)
                    self.logger.info("commit reviews to db")
                    session.commit()

            source.last_checked = start_date
            session.add(source)
            session.commit()
