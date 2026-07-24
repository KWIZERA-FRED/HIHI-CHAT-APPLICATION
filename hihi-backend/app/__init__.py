from flask import Flask
from app.config import DevConfig
from app.extensions import mongo, bcrypt, socketio, cors
from app.models import init_indexes
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.message import message_bp
from app import sockets

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, async_mode="threading")
    
    # Create/confirm MongoDB indexes on startup
    with app.app_context():
        init_indexes()
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(message_bp)

    @app.route("/health")
    def health_check():
        try:
            mongo.db.command("ping")
            return {"status": "ok", "db": "connected"}, 200
        except Exception as e:
            return {"status": "error", "db": str(e)}, 500

    return app
