import os

import fastapi
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.bank_parser import CBRParser
from app.database import SessionManager
from app.router import bank, model, source, text, text_result
from app.settings import Settings

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


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=400)


@app.on_event("startup")
async def startup() -> None:
    if not database_exists(Settings().database_uri_sync):
        create_database(Settings().database_uri_sync)
    # Base.metadata.create_all(bind=engine)
    path = os.path.join(os.getcwd(), "app/database/alembic.ini")
    config = Config(file_=path)
    config.attributes["configure_logger"] = False

    upgrade(config, "head")
    session_local = sessionmaker(bind=SessionManager().engine, class_=AsyncSession, expire_on_commit=False)
    async with session_local() as conn:
        await CBRParser(conn).load_banks()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
