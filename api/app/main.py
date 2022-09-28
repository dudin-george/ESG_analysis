import fastapi
from sqlalchemy_utils import create_database, database_exists  # type: ignore

from app.bank_parser import CBRParser
from app.database import SessionLocal, engine
from app.database.base import Base
from app.router import model, source, text, text_result, bank

app = fastapi.FastAPI(
    title="Texts API",
    version="0.1.0",
    description="API for DB",
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
    Base.metadata.create_all(bind=engine)
    CBRParser(SessionLocal()).load_banks()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
