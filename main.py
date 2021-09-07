from app import app, socketio, Config

if __name__ == '__main__':
    socketio.run(app, host=Config.IP_ADDRESS, debug=True)
