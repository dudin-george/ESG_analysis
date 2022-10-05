from logging import getLogger
from time import sleep
from typing import Type

import schedule  # type: ignore
from sqlalchemy_utils import create_database, database_exists  # type: ignore

from utils.arg_parser import parse_args
from utils.base_parser import BaseParser
from utils.database import Base, engine
from utils.logger import get_logger
from utils.settings import Settings


def parsers_setup(parser: type[BaseParser]) -> None:
    parser().parse()
    getLogger("schedule")
    schedule.every().day.do(parser.parse)

    while True:
        schedule.run_pending()


def main() -> None:
    sleep(5)
    logger = get_logger(__name__, Settings().logger_level)
    logger.info("start app")
    parser = parse_args()
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    logger.info("create db")
    parsers_setup(parser)


if __name__ == "__main__":
    main()
