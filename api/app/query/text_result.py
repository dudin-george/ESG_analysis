from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Model
from app.database.models.text_result import TextResult
from app.database.models.text_sentence import TextSentence
from app.exceptions import IdNotFoundError
from app.schemes.text import PostTextResultItem


async def get_text_result_items(db: AsyncSession, text_id: int) -> list[TextResult]:
    query = select(TextResult).join(TextResult.text_sentence).filter(TextSentence.text_id == text_id)
    return await db.scalars(query)  # type: ignore


async def create_text_results(db: AsyncSession, texts: list[PostTextResultItem]) -> None:
    # todo make in one query
    for text in texts:
        text_sentence = await db.get(TextSentence, text.text_sentence_id)  # todo find all text_sentences and model
        model = await db.get(Model, text.model_id)
        if text_sentence is None or model is None:
            raise IdNotFoundError("Source or bank not found")
        text_result = TextResult(
            text_sentence_id=text.text_sentence_id,
            result=text.text_result,
            model_id=text.model_id,
            is_processed=True,
        )
        await db.execute(
            update(TextResult)
            .filter(TextResult.text_sentence_id == text.text_sentence_id)
            .filter(TextResult.model_id == text.model_id)
            .values(text_result.dict())
        )
    await db.commit()
