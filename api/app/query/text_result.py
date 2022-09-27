from sqlalchemy.orm import Session

from app.database.text_result import TextResult
from app.schemes.text import PostTextResult


async def get_text_result_items(db: Session, text_id: int | None) -> list[TextResult]:
    query = db.query(TextResult)
    if text_id:
        query = query.filter(TextResult.text_sentence_id.in_(text_id))
    return query.all()


async def create_text_results(db: Session, texts: list[PostTextResult]) -> None:
    text_results = []
    for text in texts:
        text_result = TextResult(
            text_sentence_id=text.text_sentence_id,
            result=text.text_result,
            model_id=text.model_id,
        )
        text_results.append(text_result)
    db.add_all(text_results)
    db.commit()
