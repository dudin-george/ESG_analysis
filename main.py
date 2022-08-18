import threading
import time
from parser.banki_ru_reviews import BankiReviews
from parser.cbr_parser import CBRParser
from parser.sravni_reviews import SravniReviews
from typing import Callable

import schedule  # type: ignore

from db.database import create_db_and_tables
from misc.logger import get_logger
from models.model_workflow import model_parse_sentences


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main() -> None:
    time.sleep(5)  # sleep 5 sec for startup
    logger = get_logger(__name__)
    logger.info("start app")
    create_db_and_tables()
    logger.info("create db")
    CBRParser().parse()  # init bank list
    sravni_reviews = SravniReviews()
    # sravni_reviews.parse()
    # model_parse_sentences()
    banki_ru_reviews = BankiReviews()
    # banki_ru_reviews.parse()
    # run one time for init
    run_threaded(sravni_reviews.parse)  # type: ignore
    run_threaded(banki_ru_reviews.parse)  # type: ignore
    get_logger("schedule")
    schedule.every().day.do(run_threaded, model_parse_sentences)
    schedule.every().day.do(run_threaded, sravni_reviews.parse)
    schedule.every().day.do(run_threaded, banki_ru_reviews.parse)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
