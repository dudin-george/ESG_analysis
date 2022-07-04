import threading
from parser.sravni_reviews import SravniReviews
from typing import Callable

import schedule  # type: ignore
from sqlmodel import Session

from db.database import create_db_and_tables, engine
from db.models import Models
from db.text_results import TextResult
from misc.Logger import get_logger
from models.ModelSentiment import ModelSentiment


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main() -> None:
    logger = get_logger(__name__)
    logger.info("start app")
    create_db_and_tables()
    logger.info("create db")
    model = ModelSentiment("pretrained_models", "test")
    model(["test"])

    with Session(engine) as session:
        text_model = Models(model_path="test")
        text_results = TextResult(text="test", sent_num=1, result="abaavaba", model=[text_model])
        session.add(text_model)
        session.add(text_results)
        session.commit()

        session.refresh(text_model)
        session.refresh(text_results)

    sravni_parser = SravniReviews()
    sravni_parser.parse()  # run one time for init

    get_logger("schedule")
    schedule.every().minute.do(run_threaded, sravni_parser.parse)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
