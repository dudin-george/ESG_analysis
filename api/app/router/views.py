from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import conlist

from app.dependencies import Session
from app.query.views import aggregate_text_result, text_reviews_count
from app.schemes.source import SourceSitesEnum
from app.schemes.views import (
    AggregateTetResultResponse,
    IndexTypeVal,
    ReviewsCountResponse,
    SentenceCountAggregate,
)

router = APIRouter(prefix="/views", tags=["aggregate"])


@router.get("/aggregate_text_result", response_model=AggregateTetResultResponse)
async def get_aggregate_text_result(
    db: Session,
    bank_ids: Annotated[conlist(int, min_items=1), Query(description="Список id банков")],  # type: ignore[valid-type]
    model_names: Annotated[conlist(str, min_items=1), Query(description="Список названий моделей")],  # type: ignore[valid-type]
    source_type: Annotated[conlist(str, min_items=1), Query(description="Список типов источников")],  # type: ignore[valid-type]
    start_year: Annotated[
        int,
        Query(
            ge=datetime.fromtimestamp(1).year,
            le=datetime.now().year,
            description="Первый год рассматриваемого периода",
        ),
    ] = datetime.fromtimestamp(1).year,
    end_year: Annotated[
        int,
        Query(
            ge=datetime.fromtimestamp(1).year,
            le=datetime.now().year,
            description="Последний год рассматриваемого периода",
        ),
    ] = datetime.now().year,
    # todo test in request 0 elems # https://github.com/pydantic/pydantic/issues/975
    aggregate_by_year: Annotated[bool, Query(description="Типы агрегации год/квартал")] = False,
    index_type: Annotated[IndexTypeVal, Query(description="Тип индекса")] = IndexTypeVal.index_safe,
) -> AggregateTetResultResponse:
    if start_year > end_year:
        pass
    data = await aggregate_text_result(
        db,
        start_year,
        end_year,
        bank_ids,
        model_names,
        source_type,
        aggregate_by_year,
        index_type,
    )
    return AggregateTetResultResponse(items=data)


@router.get("/reviews_count", response_model=ReviewsCountResponse)
async def get_reviews_count(
    source_sites: Annotated[list[SourceSitesEnum] | None, Query(description="Список сайтов")],
    session: Session,
    start_date: Annotated[
        date,
        Query(
            ge=datetime.fromtimestamp(1).timestamp(),
            le=datetime.now().timestamp(),
            description="Начальная дата рассматриваемого периода",
        ),
    ] = datetime.fromtimestamp(1).date(),
    end_date: Annotated[
        date,
        Query(
            ge=datetime.fromtimestamp(1).timestamp(),
            le=datetime.now().timestamp(),
            description="Конечная дата рассматриваемого периода",
        ),
    ] = datetime.now().date(),
    aggregate_by: Annotated[SentenceCountAggregate, Query(description="Тип агрегации")] = SentenceCountAggregate.month,
) -> ReviewsCountResponse:
    if start_date > end_date:
        pass
    data = await text_reviews_count(session, start_date, end_date, source_sites, aggregate_by)
    return ReviewsCountResponse(items=data)
