import os

import fastapi
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists
from starlette.middleware.gzip import GZipMiddleware

from app.dataloader import load_data
from app.router import (
    bank_router,
    model_router,
    source_router,
    text_result_router,
    text_router,
    views_router,
)
from app.settings import Settings

app = fastapi.FastAPI(
    title="Texts API",
    version="0.1.0",
    description="API for DB",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(text_router)
app.include_router(model_router)
app.include_router(text_result_router)
app.include_router(source_router)
app.include_router(bank_router)
app.include_router(views_router)


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
    config.set_main_option("script_location", "app/database/alembic")
    upgrade(config, "head")
    await load_data()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
