from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base


class ModelType(Base):
    __tablename__ = "model_type"

    id = Column(Integer, primary_key=True)
    model_type = Column(String)
    models = relationship("Model", back_populates="model_type")


class Model(Base):
    __tablename__ = "model"

    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    model_type_id = Column(Integer, ForeignKey("model_type.id"))
    model_type = relationship("ModelType", back_populates="models")
    text_results = relationship("TextResult", back_populates="model")
