from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.query.source import (  # type: ignore
    create_source,
    get_source_items,
    get_source_types_items,
)
from app.shemes.source import (
    CreateSource,
    GetSource,
    GetSourceItem,
    GetSourceTypes,
    GetSourceTypesItem,
    PostSourceResponse,
)

router = APIRouter(prefix="/source", tags=["source"])


@router.get("/", response_model=GetSource)
async def get_sources(db: Session = Depends(get_db)) -> GetSource:
    source_items = await get_source_items(db)
    get_source = GetSource(items=[])
    for source_item in source_items:  # todo orm mode
        get_source_item = GetSourceItem(
            id=source_item.id,
            site=source_item.site,
            source_type_id=source_item.source_type_id,
            source_type=source_item.source_type.name,
            parser_state=source_item.parser_state,
            last_update=source_item.last_update,
        )
        get_source.items.append(get_source_item)
    return get_source


@router.post("/", response_model=PostSourceResponse)
async def post_source(source: CreateSource, db: Session = Depends(get_db)) -> PostSourceResponse:
    source_id = await create_source(db, source)
    return PostSourceResponse(source_id=source_id)


@router.get("type/", response_model=GetSourceTypes)
async def get_source_types(db: Session = Depends(get_db)) -> GetSourceTypes:
    source_types = await get_source_types_items(db)
    get_source_type = GetSourceTypes(items=[])
    for source_item in source_types:
        get_source_item = GetSourceTypesItem(id=source_item.id, name=source_item.name)
        get_source_type.items.append(get_source_item)
    return get_source_type
