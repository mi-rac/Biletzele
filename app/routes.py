from flask import render_template, flash, redirect, url_for, request
from flask_socketio import join_room
from app import app, socketio
import random
import string
import json

game_rooms = {}

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
    game_rooms[room] = {}
    game_rooms[room].setdefault('users', []).append(username)
    return render_template('lobby.html', room=room, username=username, users=game_rooms[room]['users'], host=True)

@app.route('/leave_room')
def leave_room():
    pass

@app.route('/join/<string:username>')
def join(username):
    room = request.args.get('room')
    if room:
        game_rooms[room]['users'].append(username)
        return render_template('lobby.html', room=room, username=username, users=json.dumps(game_rooms[room]['users']))
    else:
        return redirect(url_for('home', username=username))

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('update_user_list', data)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room()
    user_list = game_rooms[data['room']]['users']
    user_list.remove(data['username'])
    data['users'] = user_list
    data['url'] = url_for('home', username=data["username"])
    socketio.emit('update_user_list', data)
    socketio.emit('redirect_home', data)
