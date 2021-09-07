import eventlet
eventlet.monkey_patch()
from app import app, socketio, Config

if __name__ == '__main__':
    socketio.run(app)
