from quart import Quart, request
from models import User
from quart_saas.db import db
import asyncio

app = Quart(__name__)


# tenant detection middleware
@app.before_request
async def load_tenant():
    if request.path == "/register_tenant":
        return

    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id is None:
        tenant_id = request.args.get("tenant-id")
    if not tenant_id:
        return {"error": "X-Tenant-ID header missing"}, 400
    if tenant_id not in db.registered_tenants:
        return {"error": f"Tenant '{tenant_id}' not registered"}, 403
    request.tenant_id = tenant_id


# session lifecycle
@app.after_request
async def close_session(response):
    await db.close_session()
    return response


@app.teardown_request
async def teardown_request(exc):
    await db.commit_or_rollback(exc)


# register a tenant dynamically
@app.route("/register_tenant", methods=["POST"])
async def register_tenant():
    data = await request.get_json()
    tenant_id = data.get("tenant_id")
    if not tenant_id:
        return {"error": "tenant_id is required"}, 400
    created = await db.register_tenant(tenant_id)
    if not created:
        return {"message": f"Tenant '{tenant_id}' already exists"}, 200
    return {"message": f"Tenant '{tenant_id}' registered successfully"}, 201


# seed data for a tenant
@app.route("/seed")
async def seed():
    tenant_id = request.args.get("tenant-id")
    async with (await db.get_session()) as session:
        session.add_all([
            User(name=f"TenantUser {tenant_id}"),
            User(name=f"TenantUser 2 {tenant_id}"),
        ])
        await session.commit()
    return {"status": f"seeded for tenant {request.tenant_id}"}


# list users
@app.route("/users")
async def users():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    result = await User.paginate(page, page_size)
    return result.as_dict()


if __name__ == "__main__":
    asyncio.run(app.run_task())
