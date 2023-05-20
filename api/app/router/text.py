from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.dependencies import Session
from app.exceptions import IdNotFoundError
from app.query.text import create_text_sentences, get_text_sentences
from app.schemes.text import GetTextSentences, PostTextItem

router = APIRouter(prefix="/text", tags=["text"])


@router.get("/sentences", response_model=GetTextSentences, response_model_by_alias=False)
async def get_sentences(
    db: Session,
    sources: Annotated[list[str], Query(example=["example.com"])],
    model_id: Annotated[int, Query()],
    limit: Annotated[int, Query(description="total values")] = 100,
) -> GetTextSentences | JSONResponse:
    if len(sources) == 0 or sources[0] == "":
        # TODO add docs for exception, change to HTTPException
        return JSONResponse(status_code=400, content={"message": "sources not found"})
    sentences = await get_text_sentences(db, model_id, sources, limit)

    return GetTextSentences(items=sentences)


@router.post("/")
async def post_text(texts: PostTextItem, db: Session) -> JSONResponse:
    try:
        await create_text_sentences(db, texts)
    except IdNotFoundError as e:
        # TODO add docs for exception, change to HTTPException
        return JSONResponse(status_code=404, content={"message": str(e)})
    except Exception as e:
        # TODO add docs for exception, change to HTTPException
        return JSONResponse({"message": str(e)}, status_code=400)
    # TODO add doc for response
    return JSONResponse({"message": "OK"})
