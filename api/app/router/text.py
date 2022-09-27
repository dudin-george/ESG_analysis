from fastapi import APIRouter, Query

from app.shemes.text import GetTextSentences, PostTextItem

router = APIRouter(prefix="/text", tags=["text"])


@router.get("/sentences", response_model=GetTextSentences)
async def get_sentences(
    sources: list[str] = Query(default=["new"]), limit: int = 100, offset: int = 0
) -> dict[str, str]:
    return {"message": "OK"}


@router.post("/")
async def post_text(texts: list[PostTextItem]) -> dict[str, str]:
    return {"message": "OK"}
