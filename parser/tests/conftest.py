import asyncio
from pathlib import Path
from uuid import uuid4
import pytest
from os import environ
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from common.database import Base
from common.settings import Settings

PROJECT_PATH = Path(__file__).parent.parent.resolve()
settings = Settings()

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> str:
    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_url
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_url
    finally:
        drop_database(tmp_url)

@pytest.fixture
def engine(postgres: str) -> Engine:
    engine = create_engine(postgres, echo=True)
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture
def session_factory(engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
async def session(session_factory) -> Session:
    async with session_factory() as session:
        yield session





@pytest.fixture
def api_source() -> tuple[str, dict]:
    return f"{settings.api_url}/source/", {
                "id": 0,
                "site": "string",
                "source_type_id": 0,
                "parser_state": "string",
                "last_update": "2022-12-26T18:14:55.962Z"
            }

@pytest.fixture
def api_bank() -> tuple[str, dict]:
    return f"{settings.api_url}/bank/", {
                "items": [
                    {
                        "id": 1,
                        "bank_name": "string",
                        "licence": "1",
                        "description": "string"
                    },
                    {
                        "id": 1000,
                        "bank_name": "string",
                        "licence": "1000",
                        "description": "string"
                    }
                ]
            }
