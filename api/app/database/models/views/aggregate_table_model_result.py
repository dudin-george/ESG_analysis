from sqlalchemy import Column, Float, Integer, String

from app.database.models.base import Base


class AggregateTableModelResult(Base):
    __tablename__ = "aggregate_table_model_result"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, index=True)
    quater = Column(Integer, index=True)  # todo rename
    model_name = Column(String)
    source_site = Column(String)
    source_type = Column(String)
    bank_name = Column(String)
    bank_id = Column(Integer)
    neutral = Column(Integer)
    positive = Column(Integer)
    negative = Column(Integer)
    total = Column(Integer)
    index_base = Column(Float, default=0)
    index_mean = Column(Float, default=0)
    index_std = Column(Float, default=0)
    index_safe = Column(Float, default=0)

    def __repr__(self) -> str:
        return (
            f"AggregateTableModelResult(year={self.year}, quater={self.quater}, model_name={self.model_name},"
            f" source_site={self.source_site}, source_type={self.source_type}, bank_name={self.bank_name},"
            f" neutral={self.neutral}, positive={self.positive}, negative={self.negative}, total={self.total})"
        )
