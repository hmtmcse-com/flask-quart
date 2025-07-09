from blue.controller import Controller

bp = Controller("my_bp", url="/api")

@bp.route("/hello")
async def hello():
    return "Return"
