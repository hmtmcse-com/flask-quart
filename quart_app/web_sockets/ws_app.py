from quart import Quart, websocket, render_template, request

ws_app = Quart(__name__)
clients = set()


@ws_app.route('/')
async def index():
    return await render_template('websocket.html')


@ws_app.websocket('/ws')
async def ws():
    ws_conn = websocket._get_current_object()
    clients.add(ws_conn)
    try:
        while True:
            data = await websocket.receive()
            for client in clients:
                if client != ws_conn:
                    await client.send(f"Client said: {data}")
    finally:
        clients.remove(ws_conn)


@ws_app.route('/send')
async def send_message_to_ws():
    msg = request.args.get("msg", "")
    if not msg:
        return {"status": "error", "message": "No msg provided"}, 400

    for client in clients:
        await client.send(f"[From HTTP] {msg}")
    return {"status": "success", "message": f"Sent to {len(clients)} clients"}


if __name__ == "__main__":
    ws_app.run(debug=True)
