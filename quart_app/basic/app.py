from quart import Quart, jsonify, render_template
import asyncio

app = Quart(__name__)


# API route
@app.route("/api/data")
async def api_data():
    return jsonify({"message": "Hello from API!", "status": "success"})


@app.route("/api/sync")
def sync():
    return jsonify({"message": "Hello from Sync API!", "status": "success"})


# HTML route
@app.route("/")
async def index():
    return await render_template("index.html", title="Quart Example")


# HTML route
@app.route("/sync")
def sync_index():
    # Call Async method from none async method
    return asyncio.run(render_template("index.html", title="Sync Quart Example"))


if __name__ == "__main__":
    app.run(debug=True)
