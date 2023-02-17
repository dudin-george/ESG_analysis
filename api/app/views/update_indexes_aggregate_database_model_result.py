from sqlalchemy import Float, Integer, cast, func, select, update
from sqlalchemy.orm import Session

from app.database.models import AggregateTableModelResult as TextResultAgg
from app.misc.logger import get_logger

logger = get_logger(__name__)


def update_indexes(session: Session) -> None:
    calculate_index_base(session)
    calculate_index_mean(session)
    calculate_index_std(session)
    calculate_index_safe(session)


def calculate_index_base(session: Session) -> None:
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.total > 0)
        .values(index_base=cast((TextResultAgg.positive - TextResultAgg.negative), Float) / TextResultAgg.total)
    )
    session.commit()
    logger.info("Calculated index base")


def calculate_index_mean(session: Session) -> None:
    select_mean = select(
        TextResultAgg.id,
        func.avg(TextResultAgg.index_base)
        .over(partition_by=[TextResultAgg.source_type, TextResultAgg.model_name])
        .label("avg"),
    ).subquery("select_mean")
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.id == select_mean.c.id)
        .values(
            index_mean=select_mean.c.avg,
        )
    )
    session.commit()
    logger.info("Calculated index mean")


def calculate_index_std(session: Session) -> None:
    eps = 1e-5
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.total > 0)
        .values(
            # (db.POS / (db.TOTAL - db.POS) / db.TOTAL**3 + db.NEG / (db.TOTAL - db.NEG) / db.TOTAL**3)**0.5
            index_std=func.sqrt(
                TextResultAgg.positive
                / (TextResultAgg.total - TextResultAgg.positive + eps)
                / func.pow(TextResultAgg.total, 3)
                + TextResultAgg.negative
                / (TextResultAgg.total - TextResultAgg.negative + eps)
                / func.pow(TextResultAgg.total, 3)
            ),
        )
    )
    session.commit()
    logger.info("Calculated index std")


def calculate_index_safe(session: Session) -> None:
    # (2 * (db['INDEX'] - db['INDEX_MEAN'] > 0) - 1) * (np.maximum(np.abs(db['INDEX'] - db['INDEX_MEAN']) - db['INDEX_STD'],0))
    # (2 * (index_base - index_mean > 0) - 1) * (max(abs(index_base - index_mean) - index_std, 0))
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.total > 0)
        .values(
            index_safe=(
                cast(
                    2
                    * cast(
                        (TextResultAgg.index_base - TextResultAgg.index_mean) > 0,
                        Integer,
                    )
                    - 1,
                    Float,
                )
                * func.greatest(
                    func.abs(TextResultAgg.index_base - TextResultAgg.index_mean) - TextResultAgg.index_std,
                    0,
                )
            )
        )
    )
    session.commit()
    logger.info("Calculated index safe")
