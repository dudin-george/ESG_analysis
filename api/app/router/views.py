from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import conlist
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.query.views import aggregate_text_result
from app.schemes.views import AggregateTetResultResponse, IndexTypeVal

router = APIRouter(prefix="/views", tags=["aggregate"])


@router.get("/aggregate_text_result", response_model=AggregateTetResultResponse)
async def get_aggregate_text_result(
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
        start_quarter: int = Query(default=1, ge=1, le=4, description="Первый квартал рассматриваемого периода"),
        end_quarter: int = Query(default=4, ge=1, le=4, description="Последний квартал рассматриваемого периода"),
        bank_ids: conlist(int, min_items=1) = Query(description="Список id банков"),  # type: ignore[valid-type]
        model_names: conlist(str, min_items=1) = Query(description="Список id моделей"),  # type: ignore[valid-type]
        source_type: conlist(str, min_items=1) = Query(description="Список типов источников"),
        # type: ignore[valid-type]
        # todo test in request 0 elems # https://github.com/pydantic/pydantic/issues/975
        aggregate_by_year: bool = Query(default=False, description="Типы агрегации год/квартал"),
        index_type: IndexTypeVal = Query(default=IndexTypeVal.default_index, description="Тип индекса"),
        db: AsyncSession = Depends(get_session),
) -> AggregateTetResultResponse:
    data = await aggregate_text_result(
        db,
        start_year,
        end_year,
        start_quarter,
        end_quarter,
        bank_ids,
        model_names,
        source_type,
        aggregate_by_year,
        index_type,
    )
    return AggregateTetResultResponse(items=data)
