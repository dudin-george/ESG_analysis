from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.text_result import TextResult


class ModelType(Base):
    __tablename__ = "model_type"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String, index=True)
    models: Mapped["Model"] = relationship("Model", back_populates="model_type")


class Model(Base):
    __tablename__ = "model"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)
    model_type_id = Column(Integer, ForeignKey("model_type.id"), index=True)
    model_type: Mapped["ModelType"] = relationship("ModelType", back_populates="models")
    text_results: Mapped["TextResult"] = relationship("TextResult", back_populates="model")
