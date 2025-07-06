from quart import Quart
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from saas.models import load
from saas.orm.saas_orm import saas_orm

saas_app = Quart(__name__)



engine = create_async_engine("sqlite+aiosqlite:///example1.db", echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

load()

@saas_app.before_serving
async def startup():
    await saas_orm.create_drop_all_model()


if __name__ == "__main__":
    saas_app.run(debug=True)
