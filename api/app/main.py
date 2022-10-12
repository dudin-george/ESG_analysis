# from app.database.models.base import Base
import os

import fastapi
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists

from app.bank_parser import CBRParser
from app.database import SessionLocal, engine
from app.router import bank, model, source, text, text_result

app = fastapi.FastAPI(
    title="Texts API",
    version="0.1.0",
    description="API for DB",
    debug=True,
)
app.include_router(text.router)
app.include_router(model.router)
app.include_router(text_result.router)
app.include_router(source.router)
app.include_router(bank.router)


@app.on_event("startup")
def startup() -> None:
    if not database_exists(engine.url):
        create_database(engine.url)
    # Base.metadata.create_all(bind=engine)
    path = os.path.join(os.getcwd(), "app/database/alembic.ini")
    upgrade(Config(path), "head")
    CBRParser(SessionLocal()).load_banks()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
