from sqlalchemy import and_, case, delete, extract, func, insert, select
from sqlalchemy.orm import Session

from app.database import (
    AggregateTableModelResult,
    Bank,
    BankType,
    Model,
    Source,
    SourceType,
    Text,
    TextResult,
    TextSentence,
)
from app.misc.logger import get_logger

logger = get_logger(__name__)


def recalculate_aggregate_table(session: Session) -> None:
    session.execute(delete(AggregateTableModelResult))
    session.execute("ALTER SEQUENCE aggregate_table_model_result_id_seq RESTART WITH 1")  # type: ignore
    session.commit()


def aggregate_database_sentiment(session: Session) -> None:
    """
    select
        extract(year from text.date) as year,
        extract(QUARTER from text.date) as quarter,
        bank.id as "bank_id",
        model.name as "model_name",
        source.site as "source_site",
        source_type.name as "source_type_name",
        sum(positive) as "positive",
        sum(neutral) as "neutral",
        sum(negative) as "negative",
        sum(positive+neutral+negative) as total from
        (select
          text_sentence_id,
          model_id,
          case when (log_positive > log_neutral) and (log_positive > log_negative) then 1 else 0 end as "positive",
          case when (log_neutral > log_positive) and (log_neutral > log_negative) then 1 else 0 end as "neutral",
          case when (log_negative > log_neutral) and (log_negative > log_positive) then 1 else 0 end as "negative"
        from (
          SELECT
            text_sentence_id,
            model_id,
            (LOG(result[1]+0.0000001)) as "log_neutral",
            (LOG(result[2]+0.0000001)) as "log_positive",
            (LOG(result[3]+0.0000001)) as "log_negative"
          FROM text_result
          where model_id = 1) t) pos_neut_neg
    JOIN
      text_sentence ON pos_neut_neg.text_sentence_id = text_sentence.id
    JOIN
      text ON text_sentence.text_id = text.id
    JOIN
      bank ON text.bank_id = bank.id
    JOIN
      source ON source.id = text.source_id
    JOIN
      source_type ON source.source_type_id = source_type.id
    JOIN
      model ON model.id = pos_neut_neg.model_id
    GROUP BY quarter, year, source.site, source_type.name, bank.id, model.name
    """
    eps = 1e-7

    select_log_result = (
        select(
            TextResult.text_sentence_id,
            TextResult.model_id,
            func.log(TextResult.result[1] + eps).label("log_neutral"),
            func.log(TextResult.result[2] + eps).label("log_positive"),
            func.log(TextResult.result[3] + eps).label("log_negative"),
        )
        .where(TextResult.model_id == 1)
        .subquery()
    )
    select_pos_neut_neg = select(
        select_log_result.c.text_sentence_id,
        select_log_result.c.model_id,
        case(
            (
                and_(
                    select_log_result.c.log_positive > select_log_result.c.log_neutral,
                    select_log_result.c.log_positive > select_log_result.c.log_negative,
                ),
                1,
            ),
            else_=0,
        ).label("positive"),
        case(
            (
                and_(
                    select_log_result.c.log_neutral > select_log_result.c.log_positive,
                    select_log_result.c.log_neutral > select_log_result.c.log_negative,
                ),
                1,
            ),
            else_=0,
        ).label("neutral"),
        case(
            (
                and_(
                    select_log_result.c.log_negative > select_log_result.c.log_neutral,
                    select_log_result.c.log_negative > select_log_result.c.log_positive,
                ),
                1,
            ),
            else_=0,
        ).label("negative"),
    ).subquery()
    query = (
        select(
            Bank.id,
            Bank.bank_name,
            extract("quarter", Text.date).label("quarter"),
            extract("year", Text.date).label("year"),
            Model.name,
            Source.site,
            SourceType.name,
            func.sum(select_pos_neut_neg.c.positive).label("positive"),
            func.sum(select_pos_neut_neg.c.neutral).label("neutral"),
            func.sum(select_pos_neut_neg.c.negative).label("negative"),
            func.sum(
                select_pos_neut_neg.c.positive + select_pos_neut_neg.c.neutral + select_pos_neut_neg.c.negative
            ).label("total"),
        )
        .select_from(select_pos_neut_neg)
        .join(TextSentence)
        .join(Text)
        .join(Bank)
        .join(BankType)
        .join(Source)
        .join(SourceType)
        .join(Model)
        .group_by(
            "year",
            "quarter",
            Bank.id,
            Bank.bank_name,
            BankType.name,
            SourceType.name,
            Source.site,
            Model.name,
        )
    )
    session.execute(
        insert(AggregateTableModelResult).from_select(
            [
                AggregateTableModelResult.bank_id,
                AggregateTableModelResult.bank_name,
                AggregateTableModelResult.quater,
                AggregateTableModelResult.year,
                AggregateTableModelResult.model_name,
                AggregateTableModelResult.source_site,
                AggregateTableModelResult.source_type,
                AggregateTableModelResult.positive,
                AggregateTableModelResult.neutral,
                AggregateTableModelResult.negative,
                AggregateTableModelResult.total,
            ],
            query,
        )
    )
    session.commit()
    logger.info("AggregateTableModelResult table updated sentiment")


def aggregate_database_mdf(session: Session) -> None:
    eps = 1e-7

    select_log_result = (
        select(
            TextResult.text_sentence_id,
            TextResult.model_id,
            func.log(TextResult.result[1] + eps).label("log_positive"),
            func.log(TextResult.result[2] + eps).label("log_negative"),
        )
        .where(TextResult.model_id == 1)
        .subquery()
    )
    select_pos_neut_neg = select(
        select_log_result.c.text_sentence_id,
        select_log_result.c.model_id,
        case(
            (
                select_log_result.c.log_positive > select_log_result.c.log_negative,
                1,
            ),
            else_=0,
        ).label("positive"),
        case(
            (
                select_log_result.c.log_negative > select_log_result.c.log_positive,
                1,
            ),
            else_=0,
        ).label("negative"),
    ).subquery()
    query = (
        select(
            Bank.id,
            Bank.bank_name,
            extract("quarter", Text.date).label("quarter"),
            extract("year", Text.date).label("year"),
            Model.name,
            Source.site,
            SourceType.name,
            func.sum(select_pos_neut_neg.c.positive).label("positive"),
            func.sum(select_pos_neut_neg.c.negative).label("negative"),
            func.sum(select_pos_neut_neg.c.positive + select_pos_neut_neg.c.negative).label("total"),
        )
        .select_from(select_pos_neut_neg)
        .join(TextSentence)
        .join(Text)
        .join(Bank)
        .join(BankType)
        .join(Source)
        .join(SourceType)
        .join(Model)
        .group_by(
            "year",
            "quarter",
            Bank.id,
            Bank.bank_name,
            BankType.name,
            SourceType.name,
            Source.site,
            Model.name,
        )
    )
    session.execute(
        insert(AggregateTableModelResult).from_select(
            [
                AggregateTableModelResult.bank_id,
                AggregateTableModelResult.bank_name,
                AggregateTableModelResult.quater,
                AggregateTableModelResult.year,
                AggregateTableModelResult.model_name,
                AggregateTableModelResult.source_site,
                AggregateTableModelResult.source_type,
                AggregateTableModelResult.positive,
                AggregateTableModelResult.negative,
                AggregateTableModelResult.total,
            ],
            query,
        )
    )
    session.commit()
    logger.info("AggregateTableModelResult table updated mdf")
