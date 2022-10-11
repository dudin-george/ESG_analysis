from sqlalchemy.orm import Session

from app.database.models.model import Model, ModelType
from app.schemes.model import PostModel


async def get_model_items(db: Session) -> list[Model]:
    return db.query(Model).all()


async def create_model(db: Session, post_model: PostModel) -> int:
    model = db.query(Model).filter(Model.name == post_model.model_name).first()
    if model:
        model_id = model.id  # type: int
        return model_id

    model_type = db.query(ModelType).filter(ModelType.model_type == post_model.model_type).first()
    if model_type is None:
        model_type = ModelType(model_type=post_model.model_type)
    model = Model(name=post_model.model_name, model_type=model_type)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model.id  # type: ignore


async def get_model_types_items(db: Session) -> list[ModelType]:
    return db.query(ModelType).all()
