import os

from sqlalchemy.future import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from model.sourse import Source


class Database:
    __DATABASE_URL = os.environ["CONNECTION"]
    __engine = create_engine(__DATABASE_URL)  # echo=True

    def __init__(self) -> None:
        SQLModel.metadata.create_all(self.__engine)
        sravni = Source(name="sravni.ru reviews")

        with Session(self.get_engine()) as session:
            if len(session.exec(select(Source).where(Source.name == sravni.name)).all()) == 0:
                session.add(sravni)
            session.commit()

    def get_engine(self) -> Engine:
        return self.__engine
