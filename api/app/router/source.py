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
    GetSourceItem,
    GetSourceTypes,
    PatchSource,
    Source,
    SourceTypes,
)

router = APIRouter(prefix="/source", tags=["source"])


@router.get("/", response_model=GetSource)
async def get_sources(db: AsyncSession = Depends(get_session)) -> GetSource:
    source_items = await get_source_items(db)
    get_source_response_item = GetSource(items=[])
    for source_item in source_items:
        get_source_item = GetSourceItem(
            id=source_item.id,
            site=source_item.site,
            source_type_id=source_item.source_type_id,
            source_type=source_item.source_type.name,
            parser_state=source_item.parser_state,
            last_update=source_item.last_update,
        )
        get_source_response_item.items.append(get_source_item)
    return get_source_response_item


@router.post("/", response_model=Source)
async def post_source(source: CreateSource, db: AsyncSession = Depends(get_session)) -> Source:
    items = await create_source(db, source)
    return items  # type: ignore


@router.get("/item/{source_id}", response_model=Source)
async def get_source(source_id: int, db: AsyncSession = Depends(get_session)) -> Source | JSONResponse:
    source_item = await get_source_item_by_id(db, source_id)
    if source_item is None:
        return JSONResponse(status_code=404, content={"detail": "Source not found"})
    return Source.from_orm(source_item)


@router.patch("/item/{source_id}", response_model=Source)
async def patch_source(
    source_id: int, patch_source_item: PatchSource, db: AsyncSession = Depends(get_session)
) -> Source | JSONResponse:
    if patch_source_item.parser_state is None and patch_source_item.last_update is None:
        return JSONResponse(status_code=400, content={"detail": "Bad request"})
    source_item = await patch_source_by_id(db, source_id, patch_source_item)
    if source_item is None:
        return JSONResponse(status_code=404, content={"detail": "Source not found"})
    return Source.from_orm(source_item)


@router.get("/type/", response_model=GetSourceTypes)
async def get_source_types(db: AsyncSession = Depends(get_session)) -> GetSourceTypes:
    source_types = await get_source_types_items(db)
    # todo refactor
    get_source_type = GetSourceTypes(items=[])
    for source_item in source_types:
        get_source_item = SourceTypes.from_orm(source_item)
        get_source_type.items.append(get_source_item)
    return get_source_type
