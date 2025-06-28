from quart import Quart, request
from models import User
from quart_orm1.db import db

app = Quart(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite+aiosqlite:///orm-example.sqlite3",
    SQLALCHEMY_ECHO=True,
)

db.init_app(app)

@app.route("/users")
async def list_users():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    result = await User.paginate(page, page_size)
    return result.as_dict()


@app.route("/users/filter")
async def filter_users():
    name = request.args.get("name")
    if not name:
        return {"error": "Missing 'name' parameter"}, 400

    users_named_alice = await User.filter_by(name=name)
    users_data = [user.as_dict() for user in users_named_alice]

    return {"users": users_data}

@app.route("/seed")
async def seed():
    async with db.transaction() as session:
        session.add_all([
            User(name="Alice"),
            User(name="Bob"),
            User(name="Charlie"),
        ])
    return {"status": "seeded"}

if __name__ == "__main__":
    import asyncio
    async def run():
        async with db.engine.begin() as conn:
            await conn.run_sync(db.Model.metadata.create_all)
        await app.run_task()
    asyncio.run(run())
