from contextvars import ContextVar
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from saas.orm.orm_actions import ORMActions
from saas.orm.orm_data import DBConnectionData
from saas.orm.orm_properties import ORMProperties

_orm_session_context: ContextVar[Optional[AsyncSession]] = ContextVar("orm_session_context", default=None)
class SaaSORM(ORMProperties, ORMActions):

    def __init__(self):
        self.connection_data: dict[str, DBConnectionData] = {}

    def get_engine(self, db_key: str = None):
        connection_data: DBConnectionData = self.get_engine_connection_data(db_key=db_key)

        if connection_data is None:
            pass  # Raise exception

        engine = create_async_engine(
            connection_data.uri,
            echo=connection_data.printLog,
            pool_pre_ping=connection_data.poolPrePing,
            pool_size=connection_data.poolSize,
            max_overflow=connection_data.maxOverflow,
            pool_timeout=connection_data.poolTimeout,
            pool_recycle=connection_data.poolRecycle,
            future=connection_data.future,
        )
        return engine

    def get_session_maker(self, db_key: str = None):
        connection_data: DBConnectionData = self.get_engine_connection_data(db_key=db_key)

        if connection_data is None:
            pass  # Raise exception
        engine = self.get_engine(db_key=db_key)
        session_maker = async_sessionmaker(bind=engine, expire_on_commit=connection_data.expireOnCommit)
        return session_maker

    async def get_session(self, db_key: str = None) -> AsyncSession:
        session = _orm_session_context.get()
        if session is None:
            session_maker = self.get_session_maker(db_key=db_key)
            session = session_maker()
            _orm_session_context.set(session)
        return session

    async def close_session(self):
        session = _orm_session_context.get()
        if session:
            await session.close()
        _orm_session_context.set(None)


saas_orm = SaaSORM()
