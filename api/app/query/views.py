from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AggregateTableModelResult as TextResultAgg
from app.schemes.views import AggregateTextResultItem, IndexTypeVal


def get_index(index_type: IndexTypeVal) -> Any:
    match index_type:
        case IndexTypeVal.index_base:
            return TextResultAgg.index_base
        case IndexTypeVal.index_std:
            return TextResultAgg.index_std
        case IndexTypeVal.index_mean:
            return TextResultAgg.index_mean
        case IndexTypeVal.index_safe:
            return TextResultAgg.index_safe
        case _:
            raise ValueError


def aggregate_columns(aggregate_by_year: bool) -> list[Any]:
    if aggregate_by_year:
        aggregate_cols = [TextResultAgg.year, TextResultAgg.quater]
    else:
        aggregate_cols = [TextResultAgg.quater, TextResultAgg.year]
    aggregate_cols.extend(
        [TextResultAgg.source_type, TextResultAgg.model_name, TextResultAgg.bank_name, TextResultAgg.bank_id]
    )
    return aggregate_cols


async def aggregate_text_result(
    session: AsyncSession,
    start_year: int,
    end_year: int,
    bank_ids: list[int],
    model_names: list[str],
    source_types: list[str],
    aggregate_by_year: bool,
    index_type: IndexTypeVal,
) -> list[AggregateTextResultItem]:
    index_val = get_index(index_type)
    aggregate_cols = aggregate_columns(aggregate_by_year)
    query = (
        select(
            TextResultAgg.year,
            TextResultAgg.quater,
            TextResultAgg.bank_name,
            TextResultAgg.bank_id,
            TextResultAgg.model_name,
            TextResultAgg.source_type,
            func.sum(index_val).label("index"),
        )
        .where(
            TextResultAgg.year.between(start_year, end_year),
            TextResultAgg.model_name.in_(model_names),
            TextResultAgg.source_type.in_(source_types),
            TextResultAgg.bank_id.in_(bank_ids),
        )
        .group_by(*aggregate_cols)
        .order_by(TextResultAgg.year, TextResultAgg.quater)
    )
    return [
        AggregateTextResultItem.construct(  # don't validate data
            _fields_set=AggregateTextResultItem.__fields_set__,
            year=row["year"],
            quarter=row["quater"],
            date=date(row["year"], row["quater"] * 3, 1),
            bank_id=row["bank_id"],
            bank_name=row["bank_name"],
            model_name=row["model_name"],
            source_type=row["source_type"],
            index=row["index"],
        )
        for row in await session.execute(query)
    ]
