from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.query.text import create_text_sentences, get_text_sentences
from app.schemes.text import GetTextSentences, PostTextItem

router = APIRouter(prefix="/text", tags=["text"])


@router.get("/sentences", response_model=GetTextSentences)
async def get_sentences(
    sources: list[str] = Query(default=["new"]),
    model_id: int = Query(),
    limit: int = 100,
    db: Session = Depends(get_db),
) -> GetTextSentences:
    sentences = await get_text_sentences(db, model_id, sources, limit)
    return GetTextSentences(items=sentences)


@router.post("/")
async def post_text(texts: PostTextItem, db: Session = Depends(get_db)) -> JSONResponse:
    try:
        await create_text_sentences(db, texts)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)
    return JSONResponse({"message": "OK"})
