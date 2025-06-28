
curl -X POST http://localhost:5000/register_tenant?tenant-id=tenant1 -H "Content-Type: application/json" -d '{"tenant_id":"tenant1"}'
curl "http://127.0.0.1:5000/seed?tenant-id=tenant1"
curl "http://localhost:5000/users?tenant-id=tenant1"
