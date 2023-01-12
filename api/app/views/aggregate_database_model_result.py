from sqlalchemy import and_, case, extract, func, select

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
    get_sync,
)


def aggregate_database_sentiment() -> None:
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
    session = get_sync()
    select_log_result = (
        select(
            TextResult.text_sentence_id,
            TextResult.model_id,
            func.log(TextResult.result[1] + 0.0000001).label("log_neutral"),
            func.log(TextResult.result[2] + 0.0000001).label("log_positive"),
            func.log(TextResult.result[3] + 0.0000001).label("log_negative"),
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
            "quarter", "year", Text.date, Text.id, Source.site, SourceType.name, Bank.id, Model.name, BankType.name
        )
    )
    data = []
    for row in session.execute(query):
        data.append(
            AggregateTableModelResult(
                bank_name=row[0],
                bank_id=row[0],
                year=row[2],
                quater=row[1],
                model_name=row[3],
                source_site=row[4],
                source_type=row[5],
                positive=row[6],
                neutral=row[7],
                negative=row[8],
                total=row[9],
            )
        )
    session.add_all(data)
    session.commit()
    print("Done")


def aggregate_database_mdf() -> None:
    session = get_sync()
    select_log_result = (
        select(
            TextResult.text_sentence_id,
            TextResult.model_id,
            func.log(TextResult.result[1] + 0.0000001).label("log_positive"),
            func.log(TextResult.result[2] + 0.0000001).label("log_negative"),
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
            "quarter", "year", Text.date, Text.id, Source.site, SourceType.name, Bank.id, Model.name, BankType.name
        )
    )
    data = []
    for row in session.execute(query):
        data.append(
            AggregateTableModelResult(
                bank_name=row[0],
                bank_id=row[0],
                year=row[2],
                quater=row[1],
                model_name=row[3],
                source_site=row[4],
                source_type=row[5],
                positive=row[6],
                negative=row[7],
                neutral=0,
                total=row[8],
            )
        )
    session.add_all(data)
    session.commit()
    print("Done")
