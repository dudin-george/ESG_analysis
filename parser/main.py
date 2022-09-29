import threading
from typing import Callable

import schedule  # type: ignore
from sqlalchemy_utils import create_database, database_exists  # type: ignore

from database import Base, engine
from misc.logger import get_logger
from parsers.banki_ru_reviews import BankiReviews
from parsers.sravni_reviews import SravniReviews


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def parsers_setup() -> None:
    sravni_reviews = SravniReviews()
    banki_ru_reviews = BankiReviews()
    run_threaded(sravni_reviews.parse)  # type: ignore
    run_threaded(banki_ru_reviews.parse)  # type: ignore
    get_logger("schedule")
    schedule.every().day.do(run_threaded, sravni_reviews.parse)
    schedule.every().day.do(run_threaded, banki_ru_reviews.parse)

    while True:
        schedule.run_pending()


def main() -> None:
    logger = get_logger(__name__)
    logger.info("start app")
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    logger.info("create db")
    parsers_setup()


if __name__ == "__main__":
    main()
