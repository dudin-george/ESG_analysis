from parser.SravniReviews import SravniReviews
import schedule
from model.Database import Database
import threading
from typing import Callable
from misc.Logger import get_logger


def run_threaded(job_func: Callable) -> None:
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
