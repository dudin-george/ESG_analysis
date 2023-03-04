from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class AggregateTableModelResult(Base):
    __tablename__ = "aggregate_table_model_result"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(index=True)
    quater: Mapped[int] = mapped_column(index=True)
    model_name: Mapped[str]
    source_site: Mapped[str]
    source_type: Mapped[str]
    bank_name: Mapped[str]
    bank_id: Mapped[int]
    neutral: Mapped[int]
    positive: Mapped[int]
    negative: Mapped[int]
    total: Mapped[int]
    index_base: Mapped[float] = mapped_column(default=0)
    index_mean: Mapped[float] = mapped_column(default=0)
    index_std: Mapped[float] = mapped_column(default=0)
    index_safe: Mapped[float] = mapped_column(default=0)

    def __repr__(self) -> str:
        return (
            f"AggregateTableModelResult(year={self.year}, quater={self.quater}, model_name={self.model_name},"
            f" source_site={self.source_site}, source_type={self.source_type}, bank_name={self.bank_name},"
            f" neutral={self.neutral}, positive={self.positive}, negative={self.negative}, total={self.total})"
        )
