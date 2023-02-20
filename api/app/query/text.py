from datetime import datetime

from fastapi.logger import logger
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Bank, Source, Text, TextResult, TextSentence
from app.exceptions import IdNotFoundError
from app.schemes.text import GetTextSentencesItem, PostTextItem
from app.tasks.transform_texts import transform_texts


async def create_text_sentences(db: AsyncSession, post_texts: PostTextItem) -> None:
    text_db = []

    for text in post_texts.items:
        text_db_item = Text(
            link=text.link,
            source_id=text.source_id,
            date=text.date.replace(tzinfo=None),
            title=text.title,
            bank_id=text.bank_id,
            comment_num=text.comments_num,
        )
        source = await db.scalar(select(Source).filter(Source.id == text_db_item.source_id))
        bank = await db.scalar(select(Bank).filter(Bank.id == text_db_item.bank_id))
        if source is None or bank is None:
            raise IdNotFoundError("Source or bank not found")
        text_db.append(text_db_item)
        if len(text_db) > 0:
            if post_texts.parser_state:
                source.parser_state = post_texts.parser_state
            if post_texts.date:
                source.last_update = post_texts.date.replace(tzinfo=None)
            db.add(source)
    db.add_all(text_db)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e
    ids = [text_db_item.id for text_db_item in text_db]
    texts = [text.text for text in post_texts.items]
    if len(texts) == 0 or len(ids) == 0:
        return None
    time = datetime.now()
    await transform_texts(ids, texts, db)  # type: ignore
    logger.info(f"time for transform {len(ids)} sentences: {datetime.now() - time}")


async def insert_new_sentences(db: AsyncSession, model_id: int, sources: list[str]) -> None:
    text_result_subq = select(TextResult).filter(TextResult.model_id == model_id).subquery()
    query = (
        select(TextSentence.id, model_id, False)
        .join(TextSentence.text)
        .join(Text.source)
        .join(text_result_subq, TextSentence.id == text_result_subq.c.text_sentence_id, isouter=True)
        .filter(Source.site.in_(sources))
        .filter(text_result_subq.c.text_sentence_id == None)  # noqa: E711
        .limit(100_000)
    )
    await db.execute(
        insert(TextResult).from_select(
            [TextResult.text_sentence_id, TextResult.model_id, TextResult.is_processed], query
        )
    )
    await db.commit()


async def select_sentences(db: AsyncSession, model_id: int, limit: int) -> list[tuple[int, str]]:
    select_unused_sentence_ids = (
        select(TextResult.text_sentence_id, TextResult.id)
        .filter(TextResult.model_id == model_id)
        .filter(TextResult.is_processed == False)  # noqa: E712
        .limit(limit)
    ).subquery()
    query = select(TextSentence.id, TextSentence.sentence, select_unused_sentence_ids.c.id).join(
        select_unused_sentence_ids, TextSentence.id == select_unused_sentence_ids.c.text_sentence_id
    )
    return (await db.execute(query)).all()  # type: ignore


async def get_text_sentences(
    db: AsyncSession, model_id: int, sources: list[str], limit: int
) -> list[GetTextSentencesItem]:
    selected_sentences = await select_sentences(db, model_id, limit)
    if len(selected_sentences) == 0:
        await insert_new_sentences(db, model_id, sources)
        selected_sentences = await select_sentences(db, model_id, limit)
    # todo insert texts by id
    return [
        GetTextSentencesItem(sentence_id=sentence_id, sentence=sentence)
        for (sentence_id, sentence) in selected_sentences
    ]
