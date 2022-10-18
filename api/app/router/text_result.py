from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.query.text_result import create_text_results, get_text_result_items
from app.schemes.text import GetTextResult, GetTextResultItem, PostTextResult

router = APIRouter(prefix="/text_result", tags=["text_result"])


@router.get("/item/{text_id}", response_model=GetTextResult)
async def get_text_results(text_id: int, db: AsyncSession = Depends(get_session)) -> GetTextResult:
    texts = await get_text_result_items(db, text_id)
    get_text_result = GetTextResult(items=[])
    for text in texts:
        text_result = GetTextResultItem(
            id=text.id,
            text_sentence_id=text.text_sentence_id,
            result=text.result,
            model_id=text.model_id,
        )
        get_text_result.items.append(text_result)
    return get_text_result


@router.post("/")
async def post_text_result(texts: PostTextResult, db: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await create_text_results(db, texts.items)
    return {"message": "OK"}
