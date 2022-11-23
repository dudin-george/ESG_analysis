from sqlalchemy import Column, Integer, String

from app.database.models.base import Base


class AggregateTableModelResult(Base):
    __tablename__ = "aggregate_table_model_result"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, index=True)
    quater = Column(Integer, index=True)
    model_name = Column(String)
    source_site = Column(String)
    source_type = Column(String)
    bank_name = Column(String)
    neutral = Column(Integer)
    positive = Column(Integer)
    negative = Column(Integer)
    total = Column(Integer)

    def __repr__(self) -> str:
        return (
            f"AggregateTableModelResult(year={self.year}, quater={self.quater}, model_name={self.model_name},"
            f" source_site={self.source_site}, source_type={self.source_type}, bank_name={self.bank_name},"
            f" neutral={self.neutral}, positive={self.positive}, negative={self.negative}, total={self.total})"
        )
