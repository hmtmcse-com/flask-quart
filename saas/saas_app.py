from quart import Quart
from saas.models import load
from saas.orm.saas_orm import saas_orm

saas_app = Quart(__name__)

load()

@saas_app.before_serving
async def startup():
    await saas_orm.create_drop_all_model()


if __name__ == "__main__":
    saas_app.run(debug=True)
