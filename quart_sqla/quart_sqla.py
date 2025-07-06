from quart import Quart, request, jsonify, abort
from models import Base, engine, async_session, User

quart_sqla = Quart(__name__)

# create tables on startup
@quart_sqla.before_serving
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CRUD routes

# GET /users
@quart_sqla.route("/users", methods=["GET"])
async def list_users():
    async with async_session() as session:
        result = await session.execute(
            User.__table__.select()
        )
        users = result.all()
        return jsonify([dict(user._mapping) for user in users])

# GET /users/<id>
@quart_sqla.route("/users/<int:user_id>", methods=["GET"])
async def get_user(user_id):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            abort(404)
        return jsonify({"id": user.id, "name": user.name, "email": user.email})

# POST /users
@quart_sqla.route("/users", methods=["POST"])
async def create_user():
    data = await request.get_json()
    async with async_session() as session:
        user = User(name=data["name"], email=data["email"])
        session.add(user)
        await session.commit()
        return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201

# PUT /users/<id>
@quart_sqla.route("/users/<int:user_id>", methods=["PUT"])
async def update_user(user_id):
    data = await request.get_json()
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            abort(404)
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        await session.commit()
        return jsonify({"id": user.id, "name": user.name, "email": user.email})

# DELETE /users/<id>
@quart_sqla.route("/users/<int:user_id>", methods=["DELETE"])
async def delete_user(user_id):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            abort(404)
        await session.delete(user)
        await session.commit()
        return jsonify({"result": "deleted"})

if __name__ == "__main__":
    quart_sqla.run()
