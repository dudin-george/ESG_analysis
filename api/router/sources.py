from fastapi import APIRouter

from shemes import GetSource, PostSource, PostSourceResponse

router = APIRouter(prefix="/source", tags=["source"])


@router.get("/", response_model=list[GetSource])
async def get_source():
    return {"message": "OK"}


@router.post("/", response_model=PostSourceResponse)
async def post_source(model: PostSource):
    return {"model_id": 1}
