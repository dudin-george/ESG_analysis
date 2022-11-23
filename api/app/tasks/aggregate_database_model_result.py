from sqlalchemy import extract, func, select

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


def aggregate_database() -> None:
    query = (
        select(
            BankType.name,
            extract("quarter", Text.date).label("quarter"),
            extract("year", Text.date).label("year"),
            Model.name,
            Source.site,
            SourceType.name,
            func.sum(func.log(TextResult.result[1] + 0.0000001)),
            func.sum(func.log(TextResult.result[2] + 0.0000001)),
            func.sum(func.log(TextResult.result[3] + 0.0000001)),
        )
        .select_from(TextResult)
        .join(TextSentence)
        .join(Text)
        .join(Bank)
        .join(BankType)
        .join(Source)
        .join(SourceType)
        .join(Model)
        .where(Model.id == 1)
        .group_by(
            "quarter", "year", Text.date, Text.id, Source.site, SourceType.name, Bank.id, Model.name, BankType.name
        )
    )
    session = get_sync()
    data = []
    for row in session.execute(query):
        positive = row[6] if row[6] else 0
        neutral = row[7] if row[7] else 0
        negative = row[8] if row[8] else 0
        data.append(
            AggregateTableModelResult(
                bank_name=row[0],
                year=row[2],
                quater=row[1],
                model_name=row[3],
                source_site=row[4],
                source_type=row[5],
                neutral=row[6],
                positive=row[7],
                negative=row[8],
                total=positive + neutral + negative,
            )
        )
    session.add_all(data)
    session.commit()
    print("Done")
