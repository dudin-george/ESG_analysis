from datetime import datetime

from fastapi import APIRouter

from app.schemes.text import GetTextResultItem, PostTextResult

router = APIRouter(prefix="/textresult", tags=["textresult"])


@router.get("/", response_model=GetTextResultItem)
async def get_text_results(
    date: datetime | None = None, source: str | None = None, bank_id: str | None = None, text_id: int | None = None
) -> dict[str, str]:
    return {"message": "OK"}


@router.post("/")
async def post_text_result(texts: list[PostTextResult]) -> dict[str, str]:
    return {"message": "OK"}
