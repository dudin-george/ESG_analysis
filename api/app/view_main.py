import logging
import threading
from collections.abc import Callable

import schedule

from app.tasks.aggregate_database_model_result import aggregate_database


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def setup() -> None:
    logging.getLogger("schedule")
    aggregate_database()
    # schedule.every().day.do(run_threaded, aggregate_database)
    schedule.every().day.do(aggregate_database)
    while True:
        schedule.run_pending()


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
