from logging import getLogger
from time import sleep

import schedule
from sqlalchemy_utils import create_database, database_exists

from database import Base, engine
from misc.logger import get_logger
from settings import Settings
from banki_ru_reviews.reviews_parser import BankiReviews


def parsers_setup() -> None:
    banki_ru_reviews = BankiReviews()
    banki_ru_reviews.parse()
    getLogger("schedule")
    schedule.every().day.do(banki_ru_reviews.parse)

    while True:
        schedule.run_pending()


def main() -> None:
    sleep(5)
    logger = get_logger(__name__, Settings().logger_level)
    logger.info("start app")
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    logger.info("create db")
    parsers_setup()


if __name__ == "__main__":
    main()
