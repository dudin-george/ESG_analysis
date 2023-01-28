import logging

import schedule

from app.database import get_sync
from app.views import (
    aggregate_database_mdf,
    aggregate_database_sentiment,
    update_indexes,
)


def calculate_aggregate_database_sentiment() -> None:
    with get_sync() as session:
        aggregate_database_sentiment(session)
        aggregate_database_mdf(session)
        update_indexes(session)


def setup() -> None:
    calculate_aggregate_database_sentiment()
    logging.getLogger("schedule")
    schedule.every().day.do(calculate_aggregate_database_sentiment)
    while True:
        schedule.run_pending()


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
