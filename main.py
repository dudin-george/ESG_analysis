import threading
from parser.SravniReviews import SravniReviews
from typing import Callable

import schedule  # type: ignore

from misc.Logger import get_logger
from model.Database import Database


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main() -> None:
    Database()
    logger = get_logger(__name__)
    logger.info("start app")
    get_logger("schedule")

    sravni_parser = SravniReviews()
    sravni_parser.parse()  # run one time for init

    schedule.every().minute.do(run_threaded, sravni_parser.parse)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
