from flask import Flask
from config import Config
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

from app import routes, models
