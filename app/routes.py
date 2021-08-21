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
        if not username:
            return redirect(url_for('index'))
    return render_template('home.html', username=username)

@app.route('/new_lobby', methods=['GET', 'POST'])
def new_lobby():
    if request.method == "POST":
        username = request.form.get('username')
        letters = string.ascii_uppercase
        room = ''.join(random.choice(letters) for i in range(4))
        game_rooms[room] = {}
        game_rooms[room].setdefault('users', {})[username] = {}
    return redirect(url_for('lobby', room=room, username=username, host=int(True)))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == "POST":
        username = request.form.get('username')
        room = request.form.get('room')
        if not room:
            return redirect(url_for('home', username=username))
        game_rooms[room]['users'][username] = {}
    return redirect(url_for('lobby', room=room, username=username, host=int(False)))

@app.route('/lobby/<string:room>/<string:username>/<int:host>')
def lobby(room, username, host):
    return render_template('lobby.html', room=room, username=username, host=host)

@app.route('/game/<string:room>/<string:username>')
def game(room, username):
    user_list = game_rooms[room]['users']
    
    return render_template('game.html', room=room, username=username, users=user_list)

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    user_list = list(game_rooms[data['room']]['users'].keys())
    app.logger.info(user_list)
    data['users'] = json.dumps(user_list)
    socketio.emit('update_user_list', data)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    user_list = game_rooms[data['room']]['users']
    del user_list[data['username']]
    data['users'] = json.dumps(list(user_list.keys()))
    socketio.emit('update_user_list', data)

@socketio.on('start_game')
def handle_start_game_event(data):
    room = data['room']
    app.logger.info("Game starting in room {}".format(room))
    socketio.emit('redirect_start', data)

@socketio.on('choose_team')
def handle_choose_team_event(data):
    choice = data['choice']
    username = data['username']
    room = data['room']
    app.logger.info("{} chose team {}".format(username, choice))
    game_rooms[room]['users'][username]['team'] = choice
    socketio.emit('display_team_choice', data)
