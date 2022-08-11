import nltk  # type: ignore
import torch
from sqlmodel import Session, select

from db.database import engine
from db.models import Models
from db.reviews import Reviews
from db.text_results import TextResult
from misc.logger import get_logger
from models.model_sentiment import ModelSentiment


def model_parse_sentences() -> None:
    logger = get_logger("model_parse_sentence")
    logger.info("download tokenizer")
    tokenizer = nltk.data.load("tokenizers/punkt/russian.pickle")
    device = torch.device("cpu")

    with Session(engine) as session:
        models = session.exec(select(Models)).all()
        reviews = session.exec(select(Reviews).where(Reviews.processed == False)).all()  # noqa: E712

        for model in models:
            logger.info(f"process sentences with {model.model_path}")
            model_sentiment = ModelSentiment(model.model_path, device)
            logger.info(f"{model.model_path} loaded")

            for i, review in enumerate(reviews):
                logger.info(f"[{i}/{len(reviews)}] process review")
                sentences = tokenizer.tokenize(review.text)
                results = model_sentiment(sentences)
                text_results = []
                for sent_num, result in enumerate(results):
                    text_results.append(
                        TextResult(
                            sent_num=sent_num + 1, result=result.tolist(), review=review, model=[model]
                        )
                    )
                review.processed = True
                session.add_all(text_results)
                session.add(review)
                session.commit()
