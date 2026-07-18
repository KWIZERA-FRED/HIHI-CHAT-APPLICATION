from flask import Flask
from app.config import DevConfig
from app.extensions import mongo, bcrypt, socketio, cors

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, async_mode="threading")

    @app.route("/health")
    def health_check():
        try:
            mongo.db.command("ping")
            return {"status": "ok", "db": "connected"}, 200
        except Exception as e:
            return {"status": "error", "db": str(e)}, 500

    return app