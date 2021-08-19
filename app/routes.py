from flask import render_template, flash, redirect, url_for, request
from flask_socketio import join_room, leave_room
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
@app.route('/home/<string:username>', methods=['GET', 'POST'])
def home(username=None):
    if request.method == "POST":
        username = request.form.get('username')
    return render_template('home.html', username=username)

@app.route('/new_lobby', methods=['GET', 'POST'])
def new_lobby():
    if request.method == "POST":
        username = request.form.get('username')
        letters = string.ascii_uppercase
        room = ''.join(random.choice(letters) for i in range(4))
        game_rooms[room] = {}
        game_rooms[room].setdefault('users', []).append(username)
    return redirect(url_for('game', room=room, username=username, host=int(True)))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == "POST":
        username = request.form.get('username')
        room = request.form.get('room')
        if not room:
            return redirect(url_for('home', username=username))
        game_rooms[room]['users'].append(username)
    return redirect(url_for('game', room=room, username=username, host=int(False)))

@app.route('/game/<string:room>/<string:username>/<int:host>')
def game(room, username, host):
    return render_template('lobby.html', room=room, username=username, users=game_rooms[room]['users'], host=host)

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('update_user_list', data)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    user_list = game_rooms[data['room']]['users']
    user_list.remove(data['username'])
    data['users'] = user_list
    data['url'] = url_for('home', username=data["username"])
    socketio.emit('update_user_list', data)
    socketio.emit('redirect_home', data)
