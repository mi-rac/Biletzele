from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, host='192.168.0.14', debug=True)
