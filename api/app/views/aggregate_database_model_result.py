from sqlalchemy import and_, case, delete, extract, func, insert, select, text, cast, Boolean
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
    session.execute(text("ALTER SEQUENCE aggregate_table_model_result_id_seq RESTART WITH 1"))
    session.commit()


def aggregate_database_sentiment(session: Session) -> None:
    """
    SELECT EXTRACT(year FROM pos_neut_neg.date)    AS year,
           EXTRACT(QUARTER FROM pos_neut_neg.date) AS quarter,
           bank_id                                 AS bank_id,
           model.name                              AS model_name,
           source.site                             AS source_site,
           source_type.name                        AS source_type_name,
           SUM(positive)                           AS positive,
           SUM(neutral)                            AS neutral,
           SUM(negative)                           AS negative,
           SUM(positive + neutral + negative)      AS total
    FROM (SELECT pos_neut_neg_reviews.text_id,
                 pos_neut_neg_reviews.model_id,
                 pos_neut_neg_reviews.bank_id,
                 pos_neut_neg_reviews.source_id,
                 pos_neut_neg_reviews.date,
                 CASE WHEN (log_positive > log_neutral) AND (log_positive > log_negative) THEN 1 ELSE 0 END AS positive,
                 CASE WHEN (log_neutral > log_positive) AND (log_neutral > log_negative) THEN 1 ELSE 0 END  AS neutral,
                 CASE WHEN (log_negative > log_neutral) AND (log_negative > log_positive) THEN 1 ELSE 0 END AS negative
          FROM (SELECT sum(log_negative) as log_negative,
                       sum(log_positive) as log_positive,
                       sum(log_neutral)  as log_neutral,
                       text.id           as text_id,
                       text.bank_id,
                       text.source_id,
                       text.date,
                       model_id
                FROM (SELECT text_result.text_sentence_id,
                             model_id,
                             LOG(result[1] + 0.0000001) AS log_neutral,
                             LOG(result[2] + 0.0000001) AS log_positive,
                             LOG(result[3] + 0.0000001) AS log_negative
                      FROM text_result
                      WHERE model_id = 1) t
                         JOIN text_sentence ON t.text_sentence_id = text_sentence.id
                         join text ON text_sentence.text_id = text.id
                group by text.id, model_id) pos_neut_neg_reviews) pos_neut_neg
             JOIN bank ON pos_neut_neg.bank_id = bank.id
             JOIN source ON source.id = pos_neut_neg.source_id
             JOIN source_type ON source.source_type_id = source_type.id
             JOIN model ON model.id = pos_neut_neg.model_id
    GROUP BY year, quarter, source_site, source_type_name, bank_id, model_name
    """
    eps = 1e-7

    select_log_result = (
        select(
            Text.id.label("text_id"),
            Text.source_id,
            Text.bank_id,
            TextResult.model_id,
            func.sum(func.log(TextResult.result[1] + eps)).label("log_neutral"),
            func.sum(func.log(TextResult.result[2] + eps)).label("log_positive"),
            func.sum(func.log(TextResult.result[3] + eps)).label("log_negative"),
        )
        .where(TextResult.model_id == 1)
        .join(TextSentence, TextSentence.id == TextResult.text_sentence_id)
        .join(Text, Text.id == TextSentence.text_id)
        .group_by(Text.id, TextResult.model_id, Text.bank_id, Text.source_id)
        .subquery()
    )
    select_pos_neut_neg = select(
        select_log_result.c.text_id,
        select_log_result.c.model_id,
        select_log_result.c.source_id,
        select_log_result.c.bank_id,
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
        .join(Bank, Bank.id == select_pos_neut_neg.c.bank_id)
        .join(BankType)
        .join(Source, Source.id == select_pos_neut_neg.c.source_id)
        .join(SourceType)
        .join(Model, Model.id == select_pos_neut_neg.c.model_id)
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
                AggregateTableModelResult.bank_id.name,
                AggregateTableModelResult.bank_name.name,
                AggregateTableModelResult.quater.name,
                AggregateTableModelResult.year.name,
                AggregateTableModelResult.model_name.name,
                AggregateTableModelResult.source_site.name,
                AggregateTableModelResult.source_type.name,
                AggregateTableModelResult.positive.name,
                AggregateTableModelResult.neutral.name,
                AggregateTableModelResult.negative.name,
                AggregateTableModelResult.total.name,
            ],
            query,
        )
    )
    session.commit()
    logger.info("AggregateTableModelResult table updated sentiment")


def aggregate_database_mdf(session: Session, model_name: str) -> None:
    eps = 1e-7
    model_id = select(Model.id).where(Model.name == model_name).scalar_subquery()
    select_log_result = (
        select(
            Text.id.label("text_id"),
            TextResult.model_id,
            func.sum(func.log(TextResult.result[1] + eps)).label("log_positive"),
            func.sum(func.log(TextResult.result[2] + eps)).label("log_negative"),
        )
        .where(TextResult.model_id == model_id)
        .join(TextSentence, TextSentence.id == TextResult.text_sentence_id)
        .join(Text, Text.id == TextSentence.text_id)
        .group_by(Text.id, TextResult.model_id)
        .subquery()
    )
    select_pos_neut_neg = select(
        select_log_result.c.text_id,
        select_log_result.c.model_id,
        case(
            (
                cast(select_log_result.c.log_positive > select_log_result.c.log_negative, Boolean),
                1,
            ),
            else_=0,
        ).label("positive"),
        case(
            (
                cast(select_log_result.c.log_negative > select_log_result.c.log_positive, Boolean),
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
                AggregateTableModelResult.bank_id.name,
                AggregateTableModelResult.bank_name.name,
                AggregateTableModelResult.quater.name,
                AggregateTableModelResult.year.name,
                AggregateTableModelResult.model_name.name,
                AggregateTableModelResult.source_site.name,
                AggregateTableModelResult.source_type.name,
                AggregateTableModelResult.positive.name,
                AggregateTableModelResult.negative.name,
                AggregateTableModelResult.total.name,
            ],
            query,
        )
    )
    session.commit()
    logger.info(f"AggregateTableModelResult table updated {model_name}")
