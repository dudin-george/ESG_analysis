from datetime import date, datetime

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
    start_year: int = Query(
        default=datetime.fromtimestamp(1).year,
        ge=datetime.fromtimestamp(1).year,
        le=datetime.now().year,
        description="Первый год рассматриваемого периода",
    ),
    end_year: int = Query(
        default=datetime.now().year,
        ge=datetime.fromtimestamp(1).year,
        le=datetime.now().year,
        description="Последний год рассматриваемого периода",
    ),
    bank_ids: conlist(int, min_items=1) = Query(description="Список id банков"),  # type: ignore[valid-type]
    model_names: conlist(str, min_items=1) = Query(description="Список названий моделей"),  # type: ignore[valid-type]
    source_type: conlist(str, min_items=1) = Query(description="Список типов источников"),  # type: ignore[valid-type]
    # todo test in request 0 elems # https://github.com/pydantic/pydantic/issues/975
    aggregate_by_year: bool = Query(default=False, description="Типы агрегации год/квартал"),
    index_type: IndexTypeVal = Query(default=IndexTypeVal.index_base, description="Тип индекса"),
) -> AggregateTetResultResponse:
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
    session: Session,
    start_date: date = Query(
        default=datetime.fromtimestamp(1).date(),
        # ge=datetime.fromtimestamp(1).timestamp(),
        # le=datetime.now().timestamp(),
        description="Начальная дата рассматриваемого периода",
    ),
    end_date: date = Query(
        default=datetime.now().date(),
        # ge=datetime.fromtimestamp(1).timestamp(),
        # le=datetime.now().timestamp(),
        description="Конечная дата рассматриваемого периода",
    ),
    source_sites: list[SourceSitesEnum] | None = Query(description="Список сайтов"),
    # source_types: conlist(SourceTypesEnum, min_items=1) | None = Query(description="Список типов источников"),  # type: ignore[valid-type]
    aggregate_by: SentenceCountAggregate = Query(default=SentenceCountAggregate.month, description="Тип агрегации"),
) -> ReviewsCountResponse:
    data = await text_reviews_count(session, start_date, end_date, source_sites, aggregate_by)
    return ReviewsCountResponse(items=data)
