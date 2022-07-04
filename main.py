import threading
from parser.cbr_parser import CBRParser
from parser.sravni_reviews import SravniReviews
from typing import Callable

import schedule  # type: ignore

from db.database import create_db_and_tables
from misc.logger import get_logger


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main() -> None:
    logger = get_logger(__name__)
    logger.info("start app")
    create_db_and_tables()
    logger.info("create db")
    CBRParser().parse()  # init bank list
    sravni_reviews = SravniReviews()
    # run one time for init
    run_threaded(sravni_reviews.parse)  # type: ignore

    get_logger("schedule")
    schedule.every().minute.do(run_threaded, sravni_reviews.parse)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
