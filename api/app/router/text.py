from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.query.text import create_text_sentences, get_text_sentences
from app.schemes.text import GetTextSentences, PostTextItem

router = APIRouter(prefix="/text", tags=["text"])


@router.get("/sentences", response_model=GetTextSentences)
async def get_sentences(
    sources: list[str] = Query(default=["new"]), limit: int = 100, db: Session = Depends(get_db)
) -> GetTextSentences:
    sentences = await get_text_sentences(db, sources, limit)
    return GetTextSentences(items=sentences)


@router.post("/")
async def post_text(texts: PostTextItem, db: Session = Depends(get_db)) -> dict[str, str]:
    await create_text_sentences(db, texts)
    return {"message": "OK"}
