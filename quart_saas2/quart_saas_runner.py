from quart import Quart, request, jsonify
from quart_saas2.crud import CRUD
from quart_saas2.db import current_tenant_id, db
from quart_saas2.models import User

quart_saas_runner = Quart(__name__)

@quart_saas_runner.before_request
async def set_tenant():
    if request.path == "/register_tenant":
        return

    tid = request.headers.get("X-Tenant-ID")
    if tid is None:
        tid = request.args.get("tenant-id")
    if not tid:
        return jsonify({"error": "missing X-Tenant-ID"}), 400
    current_tenant_id.set(tid)

@quart_saas_runner.route("/register_tenant", methods=["POST"])
async def register():
    data = await request.get_json()
    tenant_id = data["tenant_id"]
    await db.register_tenant(tenant_id)
    return {"message": f"Tenant {tenant_id} registered."}

@quart_saas_runner.route("/users", methods=["POST"])
async def create_user():
    data = await request.json
    async with await db.get_session() as session:
        user = User(name=data["name"], email=data["email"])
        created = await CRUD.create(session, user)
        return jsonify({"id": created.id, "name": created.name})

@quart_saas_runner.route("/users", methods=["GET"])
async def list_users():
    page = int(request.args.get("page", 1))
    async with await db.get_session() as session:
        users = await CRUD.paginate(session, User, page)
        return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@quart_saas_runner.route("/users/count", methods=["GET"])
async def count_users():
    async with await db.get_session() as session:
        count = await CRUD.count(session, User)
        return {"count": count}

if __name__ == "__main__":
    quart_saas_runner.run(debug=True)
