from fastapi import APIRouter

from shemes import GetModel, PostModel, PostModelResponse

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/", response_model=list[GetModel])
async def get_model():
    return {"message": "OK"}


@router.post("/", response_model=PostModelResponse)
async def post_model(model: PostModel):
    return {"model_id": 1}
