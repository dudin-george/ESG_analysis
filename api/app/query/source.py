from sqlalchemy.orm import Session

from app.database.source import Source, SourceType
from app.schemes.source import CreateSource, PatchSource


async def get_source_items(db: Session) -> list[Source]:
    return db.query(Source).all()


async def create_source(db: Session, model: CreateSource) -> Source:
    source = db.query(Source).filter(Source.site == model.site).first()
    if source:
        return source

    source_type = db.query(SourceType).filter(SourceType.name == model.source_type).first()
    if source_type is None:
        source_type = SourceType(name=model.source_type)
    source = Source(site=model.site, source_type=source_type)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


async def get_source_item_by_id(db: Session, source_id: int) -> Source | None:
    return db.query(Source).filter(Source.id == source_id).first()


async def get_source_types_items(db: Session) -> list[SourceType]:
    return db.query(SourceType).all()


async def patch_source_by_id(db: Session, source_id: int, patch_source: PatchSource) -> Source | None:
    source = await get_source_item_by_id(db, source_id)
    if source is None:
        return None
    source.parser_state = patch_source.parser_state
    source.last_update = patch_source.last_update
    db.commit()
    db.refresh(source)
    return source
