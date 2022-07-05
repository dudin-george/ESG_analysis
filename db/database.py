import os

from sqlmodel import Session, SQLModel, create_engine, select

from db.models import Models
from db.sourse import Source

sqlite_file_name = "database.db"
database_url = os.environ["CONNECTION"]

engine = create_engine(database_url)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

    sravni = Source(name="sravni.ru reviews")
    banki_ru = Source(name="banki.ru reviews")
    models = []

    with Session(engine) as session:
        if len(session.exec(select(Source).where(Source.name == sravni.name)).all()) == 0:
            session.add(sravni)
        if len(session.exec(select(Source).where(Source.name == banki_ru.name)).all()) == 0:
            session.add(banki_ru)
        exsisting_models_path = session.exec(select(Models.model_path)).all()
        for model_path in os.listdir("pretrained_models"):
            if model_path.startswith("model") and model_path not in exsisting_models_path:
                models.append(Models(model_path=f"pretrained_models/{model_path}"))
        session.add_all(models)
        session.commit()
