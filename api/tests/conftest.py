import asyncio
from os import environ
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import requests_mock
from alembic.command import upgrade
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.database.models.bank import Bank
from app.main import app
from app.query.bank import create_bank_type, load_banks
from app.settings import Settings
from tests.utils import make_alembic_config


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
def alembic_engine(postgres):
    """
    Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    return create_async_engine(postgres, echo=True)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    """
    Проводит миграции.
    """
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def engine_async(postgres, migrated_postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine_async, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session


def relative_path(path: str) -> str:
    return f"{Path(__file__).parent}/{path}"


@pytest.fixture
async def client(session) -> AsyncClient:
    await create_bank_type(session)
    await load_banks(
        session,
        [
            Bank(id=1, bank_name="unicredit", licence="1", bank_type_id=1),
            Bank(id=1000, bank_name="vtb", licence="1000", bank_type_id=1),
        ],
    )
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

    response = await client.post(
        "/text/",
        json={
            "items": [
                {
                    "source_id": 1,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "some text",
                    "bank_id": 1,
                    "link": "string",
                    "comments_num": 0,
                }
            ],
        },
    )
    assert response.status_code == 200, response.text


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


@pytest.fixture
def mock_request() -> requests_mock.Mocker:
    with requests_mock.Mocker() as m:
        yield m


class APITestMixin:
    client: AsyncClient

    @pytest.fixture(autouse=True, scope="function")
    def use_api_client(self, client):
        self.client = client
