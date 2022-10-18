from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Bank, Source, TempSentence, Text, TextResult, TextSentence
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
        text_db.append(text_db_item)
        source = await db.scalar(select(Source).filter(Source.id == text_db_item.source_id))
        bank = await db.scalar(select(Bank).filter(Bank.id == text_db_item.bank_id))
        if source is None or bank is None:
            raise IdNotFoundError("Source or bank not found")
        if (post_texts.parser_state or post_texts.date) and len(text_db) > 0:
            source.parser_state = post_texts.parser_state
            source.last_update = post_texts.date
            db.add(source)
    db.add_all(text_db)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e
    ids = []
    for text_db_item in text_db:
        await db.refresh(text_db_item)
        ids.append(text_db_item.id)
    texts = [text.text for text in post_texts.items]
    if len(texts) == 0 or len(ids) == 0:
        return None
    time = datetime.now()
    await transform_texts(ids, texts, db)  # type: ignore
    print(f"time for transform {len(ids)} sentences: {datetime.now() - time}")  # todo logger


def _generate_table_name(model_id: int, sources: list[str]) -> str:
    return f"table_model_{model_id}_" + "_".join(sources)


async def insert_data(db: AsyncSession, model_id: int, sources: list[str], table_name: str) -> None:
    text_result_subq = select(TextResult).filter(TextResult.model_id == model_id).subquery()
    query = (
        select(TextSentence.id, TextSentence.sentence)
        .join(TextSentence.text)
        .join(Text.source)
        .join(text_result_subq, TextSentence.id == text_result_subq.c.text_sentence_id, isouter=True)
        .filter(Source.site.in_(sources))
        .filter(text_result_subq.c.text_sentence_id == None)  # noqa: E711
        .limit(100_000)
    )
    items = []
    for sentence_item in await db.scalar(query):
        items.append(
            TempSentence(sentence_id=sentence_item["id"], sentence=sentence_item["sentence"], query=table_name)
        )
    db.add_all(items)
    await db.commit()


async def get_text_sentences(
    db: AsyncSession, model_id: int, sources: list[str], limit: int
) -> list[GetTextSentencesItem]:
    text_result_subq = select(TextResult).filter(TextResult.model_id == model_id).subquery()
    query = (
        select(TextSentence.id, TextSentence.sentence)
        .join(TextSentence.text)
        .join(Text.source)
        .join(text_result_subq, TextSentence.id == text_result_subq.c.text_sentence_id, isouter=True)
        .filter(Source.site.in_(sources))
        .filter(text_result_subq.c.text_sentence_id == None)  # noqa: E711
        .limit(limit)
    )
    items = []
    for sentence in await db.execute(query):
        items.append(GetTextSentencesItem(sentence_id=sentence.id, sentence=sentence.sentence))
    return items
