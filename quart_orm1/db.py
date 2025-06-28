from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, func
from contextvars import ContextVar
from typing import Optional
from contextlib import asynccontextmanager


class AsyncSQLAlchemy:
    def __init__(self):
        self.app = None
        self.engine = None
        self.session_factory = None
        self._session_ctx: ContextVar[Optional[AsyncSession]] = ContextVar("session_ctx", default=None)
        self.Model = declarative_base()

    def init_app(self, app):
        self.app = app
        db_url = app.config.get("SQLALCHEMY_DATABASE_URI")
        if not db_url:
            raise ValueError("SQLALCHEMY_DATABASE_URI is required")

        self.engine = create_async_engine(
            db_url,
            echo=app.config.get("SQLALCHEMY_ECHO", False),
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False)

        @app.before_request
        async def before_request():
            self._session_ctx.set(None)

        @app.after_request
        async def after_request(response):
            session = self._session_ctx.get()
            if session:
                await session.close()
            self._session_ctx.set(None)
            return response

        @app.teardown_request
        async def teardown_request(exc):
            session = self._session_ctx.get()
            if session:
                try:
                    if exc is None:
                        await session.commit()
                    else:
                        await session.rollback()
                finally:
                    await session.close()
                    self._session_ctx.set(None)

    @property
    def session(self) -> AsyncSession:
        session = self._session_ctx.get()
        if session is None:
            session = self.session_factory()
            self._session_ctx.set(session)
        return session

    @asynccontextmanager
    async def transaction(self):
        session = self.session
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise


def bind_base(db: AsyncSQLAlchemy):
    Base = db.Model

    class BaseModel(Base):
        __abstract__ = True
        _db = db

        @classmethod
        async def get_all(cls):
            stmt = select(cls)
            result = await db.session.execute(stmt)
            return result.scalars().all()

        @classmethod
        async def get_by_id(cls, id_):
            stmt = select(cls).where(cls.id == id_)
            result = await db.session.execute(stmt)
            return result.scalar_one_or_none()

        @classmethod
        async def paginate(cls, page=1, page_size=10):
            stmt = select(cls).offset((page - 1) * page_size).limit(page_size)
            count_stmt = select(func.count()).select_from(cls)
            total_result = await db.session.execute(count_stmt)
            total = total_result.scalar()
            result = await db.session.execute(stmt)
            items = result.scalars().all()
            from .pagination import Paginated
            return Paginated(
                items=items,
                total=total,
                page=page,
                page_size=page_size
            )

    return BaseModel


# Create a shared db instance here for import
db = AsyncSQLAlchemy()
