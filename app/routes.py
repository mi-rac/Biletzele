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

@app.route('/chooseteam/<string:room>/<string:username>/<int:host>')
def choose_team(room, username, host):
    return render_template('choose_team.html', room=room, username=username, host=host, data=game_rooms[room])

@app.route('/enterwords/<string:room>/<string:username>/<int:host>')
def enter_words(room, username, host):
    return render_template('enter_words.html', room=room, username=username, host=host, data=game_rooms[room])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    user_list = list(game_rooms[data['room']]['users'].keys())
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
    socketio.emit('redirect_choose_team', data)

@socketio.on('choose_team')
def handle_choose_team_event(data):
    choice = data['choice']
    username = data['username']
    room = data['room']
    app.logger.info("{} chose team {}".format(username, choice))
    game_rooms[room]['users'][username]['team'] = choice
    socketio.emit('display_team_choice', data)
    try:
        if all(game_rooms[room]['users'][name]['team'] for name in game_rooms[room]['users'].keys()):
            game_rooms[room]['all_chosen'] = 1
            app.logger.info("All players chose teams in rom {}".format(room))
            socketio.emit('display_next_button', data)
    except:
        pass

@socketio.on('enter_words')
def handle_enter_words_event(data):
    room = data['room']
    app.logger.info("Get ready to enter words in room {}".format(room))
    socketio.emit('redirect_enter_words', data)
