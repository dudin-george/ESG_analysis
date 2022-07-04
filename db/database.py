import os

from sqlmodel import Session, SQLModel, create_engine, select

from db.sourse import Source

sqlite_file_name = "database.db"
database_url = os.environ["CONNECTION"]

engine = create_engine(database_url)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

    sravni = Source(name="sravni.ru reviews")
    banki_ru = Source(name="banki_ru")
    with Session(engine) as session:
        if len(session.exec(select(Source).where(Source.name == sravni.name)).all()) == 0:
            session.add(sravni)
        if len(session.exec(select(Source).where(Source.name == banki_ru.name)).all()) == 0:
            session.add(banki_ru)
        session.commit()
