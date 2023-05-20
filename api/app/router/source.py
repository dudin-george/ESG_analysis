from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.query.source import (
    create_source,
    get_source_item_by_id,
    get_source_items,
    get_source_types_items,
    patch_source_by_id,
)
from app.schemes.source import (
    CreateSource,
    GetSource,
    GetSourceItemModel,
    GetSourceTypes,
    PatchSource,
    SourceModel,
    SourceTypesModel,
)

router = APIRouter(prefix="/source", tags=["source"])


@router.get("/", response_model=GetSource)
async def get_sources(db: AsyncSession = Depends(get_session)) -> GetSource:
    source_items = await get_source_items(db)
    get_source_response_item = GetSource(
        items=[
            GetSourceItemModel(
                id=source_item.id,
                site=source_item.site,
                source_type_id=source_item.source_type_id,
                source_type=source_item.source_type.name,
                parser_state=source_item.parser_state,
                last_update=source_item.last_update,
            )
            for source_item in source_items
        ]
    )
    return get_source_response_item


@router.post("/", response_model=SourceModel)
async def post_source(source: CreateSource, db: AsyncSession = Depends(get_session)) -> SourceModel:
    source_db = await create_source(db, source)

    return SourceModel(
        id=source_db.id,
        site=source_db.site,
        source_type_id=source_db.source_type_id,
        parser_state=source_db.parser_state,
        last_update=source_db.last_update,
    )


@router.get("/item/{source_id}", response_model=SourceModel)
async def get_source(source_id: int, db: AsyncSession = Depends(get_session)) -> SourceModel | JSONResponse:
    source_item = await get_source_item_by_id(db, source_id)
    if source_item is None:
        # TODO add docs for exception, change to HTTPException
        return JSONResponse(status_code=404, content={"detail": "Source not found"})
    return SourceModel.from_orm(source_item)


@router.patch("/item/{source_id}", response_model=SourceModel)
async def patch_source(
    source_id: int, patch_source_item: PatchSource, db: AsyncSession = Depends(get_session)
) -> SourceModel | JSONResponse:
    if patch_source_item.parser_state is None and patch_source_item.last_update is None:
        # TODO add docs for exception, change to HTTPException
        return JSONResponse(status_code=400, content={"detail": "Bad request"})
    source_item = await patch_source_by_id(db, source_id, patch_source_item)
    if source_item is None:
        # TODO add docs for exception, change to HTTPException
        return JSONResponse(status_code=404, content={"detail": "Source not found"})
    return SourceModel.from_orm(source_item)


@router.get("/type/", response_model=GetSourceTypes)
async def get_source_types(db: AsyncSession = Depends(get_session)) -> GetSourceTypes:
    source_types = await get_source_types_items(db)
    get_source_type = GetSourceTypes(items=[SourceTypesModel.from_orm(source_item) for source_item in source_types])
    return get_source_type
