from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.query.model import create_model, get_model_items, get_model_types_items
from app.schemes.model import (
    GetModel,
    GetModelItem,
    GetModelType,
    ModelType,
    PostModel,
    PostModelResponse,
)

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/", response_model=GetModel)
async def get_models(db: AsyncSession = Depends(get_session)) -> GetModel:
    models = await get_model_items(db)
    get_model = GetModel(items=[])
    for model in models:
        get_model_item = GetModelItem(
            id=model.id,
            name=model.name,
            model_type_id=model.model_type_id,
            model_type=model.model_type.model_type,
        )
        get_model.items.append(get_model_item)
    return get_model


@router.post("/", response_model=PostModelResponse)
async def post_model(model: PostModel, db: AsyncSession = Depends(get_session)) -> PostModelResponse:
    model_id = await create_model(db, model)
    return PostModelResponse(model_id=model_id)


@router.get("/type/", response_model=GetModelType)
async def get_model_types(db: AsyncSession = Depends(get_session)) -> GetModelType:
    model_types = await get_model_types_items(db)
    get_model_type = GetModelType(items=[])
    for model_type in model_types:
        get_model_item = ModelType.from_orm(model_type)
        get_model_type.items.append(get_model_item)
    return get_model_type
