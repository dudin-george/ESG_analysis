from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import Source, Text, TextResult, TextSentence
from app.schemes.text import PostTextItem
from app.tasks.transform_texts import transform_texts


async def create_text_sentences(db: Session, post_texts: PostTextItem) -> None:
    text_db = []

    for text in post_texts.items:
        text_db.append(
            Text(
                link=text.link,
                source_id=text.source_id,
                date=text.date,
                title=text.title,
                bank_id=text.bank_id,
                comment_num=text.comments_num,
            )
        )
    if (post_texts.parsed_state or post_texts.date) and len(text_db) > 0:
        source = db.query(Source).filter(Source.id == text_db[0].source_id).first()
        if source is None:
            return None
        source.parser_state = post_texts.parsed_state
        source.last_update = post_texts.date
        db.add(source)
        db.commit()
    db.add_all(text_db)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise e
    ids = []
    for text_db_item in text_db:
        db.refresh(text_db_item)
        ids.append(text_db_item.id)
    texts = [text.text for text in post_texts.items]
    if len(texts) == 0 or len(ids) == 0:
        return None
    time = datetime.now()
    transform_texts(ids, texts)  # type: ignore
    print(f"time for transform {len(ids)} sentences: {datetime.now() - time}")


async def get_text_sentences(db: Session, model_id: int, sources: list[str], limit: int) -> list[TextSentence]:
    query = (
        db.query(TextSentence)
        .join(TextSentence.text)
        .join(Text.source)
        .join(TextSentence.text_results, isouter=True)
        .filter(Source.site.in_(sources))
        .filter(TextSentence.id.not_in(db.query(TextResult.text_sentence_id).filter(TextResult.model_id == model_id)))
    )
    return query.limit(limit).all()
