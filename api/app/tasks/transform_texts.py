import nltk  # type: ignore

from ..database.text_sentence import TextSentence
from sqlalchemy.orm import Session

# from . import celery_app

tokenizer = nltk.data.load("tokenizers/punkt/russian.pickle")


# @celery_app.task
def transform_texts(texts_ids: list[int], texts: list[str], db: Session) -> None:
    text_sentences = []
    for text_id, text in zip(texts_ids, texts):
        sentences = tokenizer.tokenize(text)
        for i, sentence in enumerate(sentences, 1):
            text_sentences.append(
                TextSentence(
                    text_id=text_id,
                    sentence=sentence.strip(),
                    sentence_num=i,
                )
            )
    db.add_all(text_sentences)
    db.commit()
