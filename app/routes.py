from flask import render_template, flash, redirect, url_for, request
from flask_socketio import join_room
from app import app, socketio
import random
import string

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    username = request.args.get('username')
    return render_template('home.html', username=username)

@app.route('/new_lobby/<string:username>')
def new_lobby(username):
    letters = string.ascii_uppercase
    room = ''.join(random.choice(letters) for i in range(4))
    return render_template('lobby.html', room=room, username=username, host=True)

@app.route('/leave_room')
def leave_room():
    pass

@app.route('/join')
def join():
    room = request.args.get('room')
    if room:
        return render_template('lobby.html', room=room)
    else:
        return redirect(url_for('home'))

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent a message to room {}: '{}'".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    socketio.emit('receive_message', data, room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data)
