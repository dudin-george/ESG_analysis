from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.settings import get_settings


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls) -> "SessionManager":
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(self.engine, expire_on_commit=False)

    def refresh(self) -> None:
        self.engine = create_async_engine(get_settings().database_uri, echo=True, future=True)


async def get_session() -> AsyncGenerator[Any, AsyncSession]:
    session_maker = SessionManager().get_session_maker()
    async with session_maker() as session:
        yield session


# TODO when split aggregation move this
class SyncSessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls, is_async: bool = True) -> "SyncSessionManager":
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker[Session]:
        return sessionmaker(self.engine, expire_on_commit=False, autoflush=False)

    def refresh(self) -> None:
        self.engine = create_engine(get_settings().database_uri_sync, echo=True)


def get_sync() -> Session:
    session_maker = SyncSessionManager().get_session_maker()
    return session_maker()
