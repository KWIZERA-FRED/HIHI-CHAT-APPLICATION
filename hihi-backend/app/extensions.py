from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_cors import CORS

mongo = PyMongo()
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*")
cors = CORS()