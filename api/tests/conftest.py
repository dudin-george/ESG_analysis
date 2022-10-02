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
from bs4 import BeautifulSoup
from app.database import get_db
from app.database.base import Base
from app.main import app
from app.bank_parser import CBRParser
from app.settings import Settings


class DataBase:
    engine: Engine = None
    TestingSessionLocal: sessionmaker = None


test_database = DataBase()


@pytest.fixture
def session():
    return test_database.TestingSessionLocal()


@pytest.fixture(scope="function", autouse=True)
def setup():
    test_database.engine = create_engine(Settings().database_url, echo=False)
    test_database.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_database.engine)
    if not database_exists(test_database.engine.url):
        create_database(test_database.engine.url)

    Base.metadata.create_all(bind=test_database.engine)
    yield
    drop_database(test_database.engine.url)


def override_get_db():
    db = test_database.TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def cbr_page():
    with open("html_pages/cbr_page.html", "r") as f:
        cbr_page = f.read()
    return BeautifulSoup(cbr_page, "html.parser")


@pytest.fixture
def client(mocker, cbr_page):
    mocker.patch("app.bank_parser.CBRParser.get_page", return_value=cbr_page)
    app.dependency_overrides[get_db] = override_get_db
    CBRParser(test_database.TestingSessionLocal()).load_banks()
    return TestClient(app)


@pytest.fixture
def post_source(client):
    response = client.post(
        "/source/",
        json={"site": "example.com", "source_type": "review"},
    )
    assert response.status_code == 200, response.text
