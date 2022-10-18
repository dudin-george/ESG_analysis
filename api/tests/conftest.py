import asyncio
import os
import re
from os import environ
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
from bs4 import BeautifulSoup
from configargparse import Namespace
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.database import SessionManager
from app.database.models.bank import Bank
from app.main import app
from app.query.bank import load_bank
from app.settings import Settings

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(cmd_opts: Namespace | SimpleNamespace, base_path: Path = PROJECT_PATH) -> Config:
    database_uri = Settings().database_uri_sync

    path_to_folder = cmd_opts.config
    # Change path to alembic.ini to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config + "alembic.ini")

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    # Change path to alembic folder to absolute
    alembic_location = "alembic"  # config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option("script_location", os.path.join(base_path, path_to_folder + alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", database_uri)

    return config


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> str:
    settings = Settings()

    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    cmd_options = SimpleNamespace(config="app/database/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine():
    """
    Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    settings = Settings()
    return create_async_engine(settings.database_uri_sync, echo=True)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    """
    Проводит миграции.
    """
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def engine_async(postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session


def relative_path(path: str) -> str:
    return f"{Path(__file__).parent}/{path}"


@pytest.fixture(scope="session")
def cbr_page() -> BeautifulSoup:
    path = relative_path("html_pages/cbr_page.html")
    with open(path) as f:
        cbr_page = f.read()
    return BeautifulSoup(cbr_page, "html.parser")


@pytest.fixture
def load_bank_list(cbr_page: BeautifulSoup) -> list[Bank]:
    cbr_banks = []
    for bank in cbr_page.find_all("tr")[1:]:
        items = bank.find_all("td")
        license_id_text = items[2].text
        name = re.sub("[\xa0\n\t]", " ", items[4].text)
        if license_id_text.isnumeric():
            license_id = int(license_id_text)
        else:
            license_id = int(license_id_text.split("-")[0])  # if license id with *-K, *-M, remove suffix
        cbr_banks.append(Bank(id=license_id, bank_name=name))
    return cbr_banks


@pytest.fixture
async def client(migrated_postgres, load_bank_list, manager: SessionManager = SessionManager()) -> AsyncClient:
    # utils_module.check_website_exist = AsyncMock(return_value=(True, "Status code < 400"))
    manager.refresh()
    async with manager.get_session_maker()() as session:
        await load_bank(session, [Bank(id=1, bank_name="unicredit"), Bank(id=1000, bank_name="vtb")])
        # await load_bank(session, load_bank_list)
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
        yield client


@pytest.fixture
async def post_source(client) -> None:
    response = await client.post(
        "/source/",
        json={"site": "example.com", "source_type": "review"},
    )
    assert response.status_code == 200, response.text


@pytest.fixture
async def post_model(client):
    response = await client.post("/model/", json={"model_name": "test_model", "model_type": "test_type"})
    assert response.status_code == 200, response.text


@pytest.fixture
async def post_text(client) -> None:
    response = await client.post(
        "/source/",
        json={"site": "example.com", "source_type": "review"},
    )
    assert response.status_code == 200, response.text  # async errors

    response = await client.post(
        "/text/",
        json={
            "items": [
                {
                    "source_id": 1,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": 1000,
                    "link": "string",
                    "comments_num": 0,
                }
            ],
        },
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
@pytest.fixture
async def post_text_result(client, post_model, post_text) -> None:
    response = await client.post(
        "/text_result/",
        json=[
            {
                "text_result": [0.1, 1, 3],
                "source_id": 1,
                "model_id": 1,
            }
        ],
    )
    assert response.status_code == 200, response.text
