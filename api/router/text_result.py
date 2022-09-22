from datetime import datetime

from fastapi import APIRouter

from shemes import GetTextResultItem, PostTextResult

router = APIRouter(prefix="/textresult", tags=["textresult"])


@router.get("/", response_model=GetTextResultItem)
async def get_text_results(date: datetime = None, source: str = None, bank_id: str = None,
                           text_id: int = None):
    return {"message": "OK"}


@router.post("/")
async def post_text_result(texts: list[PostTextResult]):
    return {"message": "OK"}
