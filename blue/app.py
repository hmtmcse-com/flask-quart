# app.py
from quart import Quart
from my_blueprint import bp

app = Quart(__name__)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run()
