from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AggregateTableModelResult as TextResultAgg
from app.schemes.views import AggregateTextResultItem, IndexTypeVal


async def aggregate_text_result(
        session: AsyncSession,
        start_year: int,
        end_year: int,
        start_quarter: int,
        end_quarter: int,
        bank_ids: list[int],
        model_names: list[str],
        source_types: list[str],
        aggregate_by_year: bool,
        index_type: IndexTypeVal,
) -> list[AggregateTextResultItem]:
    match index_type:
        case IndexTypeVal.default_index:
            index_val = (TextResultAgg.positive - TextResultAgg.negative) / TextResultAgg.total
        case IndexTypeVal.index_std:
            # (POS/(TOTAL-POS)/TOTAL**3+NEG/(TOTAL-NEG)/TOTAL**3)**0.5
            index_val = func.sqrt(
                TextResultAgg.positive
                / (TextResultAgg.total - TextResultAgg.positive)
                / func.pow(TextResultAgg.total, 3)
                + TextResultAgg.negative
                / (TextResultAgg.total - TextResultAgg.negative)
                / func.pow(TextResultAgg.total, 3)
            )
        case _:
            raise ValueError
    if aggregate_by_year:
        aggregate_cols = [TextResultAgg.year, TextResultAgg.quater]
    else:
        aggregate_cols = [TextResultAgg.quater, TextResultAgg.year]
    aggregate_cols.extend([TextResultAgg.source_type, TextResultAgg.model_name, TextResultAgg.bank_name])
    query = (
        select(
            TextResultAgg.year,
            TextResultAgg.quater,
            TextResultAgg.bank_name,
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
    )
    return [
        AggregateTextResultItem.construct(  # don't validate data
            _fields_set=AggregateTextResultItem.__fields_set__,
            year=row[0],
            quarter=row[1],
            date=date(row[0], row[1] * 3, 1),
            bank_name=row[2],
            model_name=row[3],
            source_type=row[4],
            index=row[5],
        )
        for row in await session.execute(query)
    ]
