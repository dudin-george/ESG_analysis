import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import (  # type: ignore
    create_database,
    database_exists,
    drop_database,
)

from app.database import get_db
from app.database.base import Base
from app.main import app
from app.settings import Settings


class DataBase:
    engine: Engine = None
    TestingSessionLocal: sessionmaker = None


database = DataBase()


@pytest.fixture(scope="function", autouse=True)
def setup():
    database.engine = create_engine(Settings().database_url, echo=False)
    database.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
    if not database_exists(database.engine.url):
        create_database(database.engine.url)

    Base.metadata.create_all(bind=database.engine)
    yield
    drop_database(database.engine.url)


def override_get_db():
    db = database.TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def post_source(client):
    response = client.post(
        "/source/",
        json={"site": "example.com", "source_type": "review"},
    )
    assert response.status_code == 200, response.text
