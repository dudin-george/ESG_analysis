from app.database.source import Source, SourceType
from sqlalchemy.orm import Session
from app.shemes import CreateSource


async def get_source_items(db: Session):
    return db.query(Source).all()


async def create_source(db: Session, model: CreateSource):
    source = db.query(Source).filter(Source.site == model.site).first()
    if source:
        return source.id

    source_type = db.query(SourceType).filter(SourceType.name == model.source_type).first()
    if source_type is None:
        source_type = SourceType(name=model.source_type)
    source = Source(site=model.site, source_type=source_type)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source.id


async def get_source_types_items(db: Session) -> list[SourceType]:
    return db.query(SourceType).all()
