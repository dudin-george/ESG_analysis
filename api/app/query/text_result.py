from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.text_result import TextResult
from app.database.models.text_sentence import TextSentence
from app.schemes.text import PostTextResultItem


async def get_text_result_items(db: AsyncSession, text_id: int) -> list[TextResult]:
    query = select(TextResult).join(TextResult.text_sentence).filter(TextSentence.text_id == text_id)
    return await db.scalars(query)  # type: ignore


async def create_text_results(db: AsyncSession, texts: list[PostTextResultItem]) -> None:
    text_results = []
    for text in texts:
        text_result = TextResult(
            text_sentence_id=text.text_sentence_id,
            result=text.text_result,
            model_id=text.model_id,
        )
        text_results.append(text_result)
    db.add_all(text_results)
    await db.commit()
