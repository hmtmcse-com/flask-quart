from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
import contextvars
import os

current_tenant_id = contextvars.ContextVar("tenant_id", default=None)

class BaseModel(DeclarativeBase):
    pass

class MultiTenantDB:
    def __init__(self):
        self.engines = {}
        self.sessions = {}
    
    async def register_tenant(self, tenant_id: str):
        db_file = f"tenants/{tenant_id}.db"
        os.makedirs("tenants", exist_ok=True)
        db_url = f"sqlite+aiosqlite:///{db_file}"
        engine = create_async_engine(db_url, echo=False)
        self.engines[tenant_id] = engine
        self.sessions[tenant_id] = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        tenant_id = current_tenant_id.get()
        if not tenant_id:
            raise RuntimeError("tenant_id is not set in context")
        if tenant_id not in self.sessions:
            await self.register_tenant(tenant_id)
        return self.sessions[tenant_id]()
    
db = MultiTenantDB()
