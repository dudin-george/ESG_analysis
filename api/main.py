import fastapi
from sqlalchemy_utils import create_database, database_exists  # type: ignore

from database import engine
from database.base import Base
from router import model, sources, text, text_result

app = fastapi.FastAPI(
    title="Texts API",
    version="0.1.0",
    description="API for DB",
)
app.include_router(text.router)
app.include_router(model.router)
app.include_router(text_result.router)
app.include_router(sources.router)


@app.on_event("startup")
def startup() -> None:
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
