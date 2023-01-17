from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.settings import get_settings


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self, is_async: bool = True) -> None:
        self.is_async = is_async
        self.refresh()

    def __new__(cls, is_async: bool = True) -> "SessionManager":
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:  # type: ignore
        if self.is_async:
            return sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        else:
            return sessionmaker(self.engine, expire_on_commit=False, autoflush=False)  # type: ignore

    def refresh(self) -> None:
        if self.is_async:
            self.engine = create_async_engine(get_settings().database_uri, echo=True, future=True)
        else:
            self.engine = create_engine(get_settings().database_uri_sync, echo=True)  # type: ignore[assignment]


async def get_session() -> AsyncSession:  # type: ignore
    session_maker = SessionManager().get_session_maker()
    async with session_maker() as session:
        yield session


def get_sync() -> Session:
    session_maker = SessionManager(is_async=False).get_session_maker()
    return session_maker()  # type: ignore
