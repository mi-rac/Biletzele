from flask import Flask
from config import Config
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, logger=True, always_connect=True, cors_allowed_origins=None)

from app import routes, models
