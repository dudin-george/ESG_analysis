from fastapi import APIRouter

from app.schemes.model import GetModel, PostModel, PostModelResponse

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/", response_model=list[GetModel])
async def get_model() -> dict[str, str]:
    return {"message": "OK"}


@router.post("/", response_model=PostModelResponse)
async def post_model(model: PostModel) -> dict[str, int]:
    return {"model_id": 1}
