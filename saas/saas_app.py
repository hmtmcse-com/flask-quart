from quart import Quart
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from saas.models import load
from saas.orm.orm_base_model import ORMBaseModel

saas_app = Quart(__name__)



engine = create_async_engine("sqlite+aiosqlite:///example1.db", echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

load()

@saas_app.before_serving
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(ORMBaseModel.metadata.create_all)


if __name__ == "__main__":
    saas_app.run(debug=True)
