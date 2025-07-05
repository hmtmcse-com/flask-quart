from quart import Quart

saas_app = Quart(__name__)

if __name__ == "__main__":
    saas_app.run(debug=True)
