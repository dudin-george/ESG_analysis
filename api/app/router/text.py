from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.exceptions import IdNotFoundError
from app.query.text import create_text_sentences, get_text_sentences
from app.schemes.text import GetTextSentences, PostTextItem

router = APIRouter(prefix="/text", tags=["text"])


@router.get("/sentences", response_model=GetTextSentences, response_model_by_alias=False)
async def get_sentences(
    sources: list[str] = Query(example=["example.com"]),
    model_id: int = Query(),
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
) -> GetTextSentences | JSONResponse:
    if len(sources) == 0 or sources[0] == "":
        return JSONResponse(status_code=400, content={"message": "sources not found"})
    sentences = await get_text_sentences(db, model_id, sources, limit)

    return GetTextSentences(
        items=sentences
    )  # [GetTextSentencesItem(sentence_id=sentence.id, sentence=sentence.sentence) for sentence in sentences]


@router.post("/")
async def post_text(texts: PostTextItem, db: AsyncSession = Depends(get_session)) -> JSONResponse:
    try:
        await create_text_sentences(db, texts)
    except IdNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": str(e)})
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)
    return JSONResponse({"message": "OK"})
