import os

from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.future import Engine
from model.Sourse import Source


class Database:
    __DATABASE_URL = os.environ["CONNECTION"]
    __engine = create_engine(__DATABASE_URL, echo=True)

    def __init__(self) -> None:
        SQLModel.metadata.create_all(self.__engine)
        sravni = Source(site="sravni.ru")

        with Session(self.get_engine()) as session:
            if len(session.exec(select(Source).where(Source.site == sravni.site)).all()) == 0:
                session.add(sravni)
            session.commit()

    def get_engine(self) -> Engine:
        return self.__engine
