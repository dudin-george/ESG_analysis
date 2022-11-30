import logging
import threading
from collections.abc import Callable

import schedule

from app.tasks.aggregate_database_model_result import aggregate_database_sentiment, aggregate_database_mdf


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def setup() -> None:
    aggregate_database_sentiment()
    aggregate_database_mdf()
    logging.getLogger("schedule")
    schedule.every().day.do(run_threaded, aggregate_database_sentiment)
    schedule.every().day.do(run_threaded, aggregate_database_mdf)
    while True:
        schedule.run_pending()


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
