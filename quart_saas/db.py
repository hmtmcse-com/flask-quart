from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, func
from contextvars import ContextVar
from typing import Optional, Dict
from contextlib import asynccontextmanager
from quart import request

Base = declarative_base()
_session_ctx: ContextVar[Optional[AsyncSession]] = ContextVar("session_ctx", default=None)

class MultiTenantSQLAlchemy:

    def __init__(self):
        self.engines: Dict[str, any] = {}
        self.sessions: Dict[str, async_sessionmaker] = {}
        self.registered_tenants = set()

    def _get_db_url(self, tenant_id: str):
        return f"sqlite+aiosqlite:///./{tenant_id}.sqlite3"

    def _create_engine_and_session(self, tenant_id: str):
        db_url = self._get_db_url(tenant_id)
        engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
        session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
        self.engines[tenant_id] = engine
        self.sessions[tenant_id] = session_factory
        return engine, session_factory

    async def register_tenant(self, tenant_id: str):
        if tenant_id in self.registered_tenants:
            return False  # already registered
        engine, _ = self._create_engine_and_session(tenant_id)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.registered_tenants.add(tenant_id)
        return True

    def get_session_factory(self, tenant_id: str) -> async_sessionmaker:
        if tenant_id not in self.sessions:
            self._create_engine_and_session(tenant_id)
        return self.sessions[tenant_id]

    async def get_session(self) -> AsyncSession:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            raise RuntimeError("Tenant ID missing in request context")
        session_factory = self.get_session_factory(tenant_id)
        session = _session_ctx.get()
        if session is None:
            session = session_factory()
            _session_ctx.set(session)
        return session

    async def close_session(self):
        session = _session_ctx.get()
        if session:
            await session.close()
        _session_ctx.set(None)

    async def commit_or_rollback(self, exc):
        session = _session_ctx.get()
        if session:
            try:
                if exc is None:
                    await session.commit()
                else:
                    await session.rollback()
            finally:
                await session.close()
                _session_ctx.set(None)

# create global db
db = MultiTenantSQLAlchemy()

def bind_base():
    class BaseModel(Base):
        __abstract__ = True

        @classmethod
        async def get_all(cls):
            session = await db.get_session()
            stmt = select(cls)
            result = await session.execute(stmt)
            return result.scalars().all()

        @classmethod
        async def get_by_id(cls, id_):
            session = await db.get_session()
            stmt = select(cls).where(cls.id == id_)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        @classmethod
        async def paginate(cls, page=1, page_size=10):
            session = await db.get_session()
            stmt = select(cls).offset((page - 1) * page_size).limit(page_size)
            count_stmt = select(func.count()).select_from(cls)
            total_result = await session.execute(count_stmt)
            total = total_result.scalar()
            result = await session.execute(stmt)
            items = result.scalars().all()
            from .pagination import Paginated
            return Paginated(
                items=items,
                total=total,
                page=page,
                page_size=page_size
            )
    return BaseModel
