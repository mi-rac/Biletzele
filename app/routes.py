from flask import render_template, flash, redirect, url_for, request
from flask_socketio import join_room, leave_room
from app import app, socketio
from app.models import Game, guest
import random
import string
import json
import time

game_data = {'BULA': guest}

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
@app.route('/home/<string:username>', methods=['GET', 'POST'])
def home(username='Guest'):
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
        game_data[room] = Game()
        game_data[room].players[username] = None
    return redirect(url_for('lobby', room=room, username=username, host=int(True)))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == "POST":
        username = request.form.get('username')
        room = request.form.get('room')
        if not room:
            return redirect(url_for('home', username=username))
        game_data[room].players[username] = None
    return redirect(url_for('lobby', room=room, username=username, host=int(False)))

@app.route('/submit_words', methods=['GET', 'POST'])
def submit_words():
    if request.method == "POST":
        username = request.form.get('username')
        room = request.form.get('room')
        for i in range(game_data[room].num_words):
            word = request.form.get(f'word{i}')
            game_data[room].words.append(word)
    return redirect(url_for('waiting', room=room, username=username))

@app.route('/lobby/<string:room>/<string:username>/<int:host>')
def lobby(room, username, host):
    return render_template('lobby.html', room=room, username=username, host=host)

@app.route('/chooseteam/<string:room>/<string:username>/<int:host>')
def choose_team(room, username, host):
    return render_template('choose_team.html', room=room, username=username, host=host, data=game_data[room])

@app.route('/enterwords/<string:room>/<string:username>/<int:host>')
def enter_words(room, username, host):
    return render_template('enter_words.html', room=room, username=username, host=host, data=game_data[room])

@app.route('/waiting/<string:room>/<string:username>')
def waiting(room, username):
    return render_template('waiting.html', room=room, username=username, data=game_data[room])

@app.route('/game/<string:room>/<string:username>', methods=['GET', 'POST'])
def game(room, username):
    return render_template('game.html', room=room, username=username, data=game_data[room])


@socketio.on('join_room')
def handle_join_room_event(data):
    room = data['room']
    username = data['username']
    app.logger.info("{} has joined the room {}".format(username, room))
    join_room(data['room'])
    players = list(game_data[room].players.keys())
    data['players'] = json.dumps(players)
    socketio.emit('update_user_list', data)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    room = data['room']
    username = data['username']
    app.logger.info("{} has left the room {}".format(username, room))
    leave_room(data['room'])
    players = list(game_data[room].players.keys())
    del user_list[username]
    data['players'] = json.dumps(players)
    socketio.emit('update_user_list', data)

@socketio.on('choose_teams')
def handle_choose_teams_event(data):
    room = data['room']
    game_data[room].stage = "choose_team"
    app.logger.info("Get ready to choose teams in room {}".format(room))
    socketio.emit('redirect_choose_team', data)

@socketio.on('choose_team')
def handle_choose_team_event(data):
    choice = data['choice']
    username = data['username']
    room = data['room']
    app.logger.info("{} chose team {}".format(username, choice))
    game_data[room].players[username] = choice
    socketio.emit('display_team_choice', data)
    try:
        if all(game_data[room].players[name] for name in game_data[room].players.keys()):
            game_data[room].all_chosen = 1
            app.logger.info("All players chose teams in room {}".format(room))
            socketio.emit('display_next_button', data)
    except:
        pass

@socketio.on('enter_words')
def handle_enter_words_event(data):
    room = data['room']
    app.logger.info("Get ready to enter words in room {}".format(room))
    for username in game_data[room].players.keys():
        color = game_data[room].players[username]
        game_data[room].teams[int(color!='red')].players.append(username)
    socketio.emit('redirect_enter_words', data)

@socketio.on('join_waiting')
def handle_join_waiting_event(data):
    room = data['room']
    app.logger.info("Updating info in waiting room {}".format(room))
    socketio.emit('update_stats', {'num_words': len(game_data[room].words),
                                        'room': room,
                                       'score': game_data[room].score})
    team = game_data[room].turn
    team_turn = game_data[room].teams[team].turn
    player = game_data[room].teams[team].players[team_turn]

    if len(game_data[room].words) + len(game_data[room].guessed) == game_data[room].num_words * len(game_data[room].players.keys()):
        app.logger.info(f"All players entered words in room {room}")
        random.shuffle(game_data[room].words)
        socketio.emit('display_next', {'room':room,
                                       'username':player})
        socketio.emit('info_waiting', {'room':room,
                                       'username':player,
                                       'color': game_data[room].players[player]})

@socketio.on('player_switch')
def handle_player_switch_event(data):
    app.logger.info("Switching Player...")
    room = data['room']

    team = game_data[room].turn
    game_data[room].turn = (team + 1) % 2

    team_player = game_data[room].teams[team].turn
    game_data[room].teams[team].turn = (team_player + 1) % len(game_data[room].teams[team].players)

    next_team = game_data[room].turn
    next_player = game_data[room].teams[next_team].turn
    username = game_data[room].teams[next_team].players[next_player]

    app.logger.info(f"{username} is next")
    random.shuffle(game_data[room].words)

    time.sleep(1)
    socketio.emit('display_next', {'room':room,
                                   'username':username})
    socketio.emit('info_waiting', {'room':room,
                                   'username':username,
                                   'color': game_data[room].players[username]})

@socketio.on('show_first_word')
def handle_show_first_word_event(data):
    app.logger.info("Getting first word...")
    room = data['room']
    word = game_data[room].words[-1]
    data['word'] = word
    socketio.emit('set_next_word', data)


@socketio.on('get_next_word')
def handle_get_next_word_event(data):
    app.logger.info("Getting next word...")
    room = data['room']
    team = game_data[room].turn
    game_data[room].guessed.append(game_data[room].words.pop())
    game_data[room].score[team] += 1

    if len(game_data[room].words) > 0:
        socketio.emit('update_stats', {'num_words': len(game_data[room].words),
                                            'room': room,
                                            'score': game_data[room].score})
        word = game_data[room].words[-1]
        data['word'] = word
        socketio.emit('set_next_word', data)
    else:
        handle_player_switch_event({'room':room})
        game_data[room].words = game_data[room].guessed
        game_data[room].guessed = []
        random.shuffle(game_data[room].words)
        socketio.emit('redirect_waiting', data)


@socketio.on('get_prev_word')
def handle_get_prev_word_event(data):
    app.logger.info("Getting previous word...")
    room = data['room']
    team = game_data[room].turn
    if len(game_data[room].guessed) != 0:
        game_data[room].words.append(game_data[room].guessed.pop())
        game_data[room].score[team] -= 1
        socketio.emit('update_stats', {'num_words': len(game_data[room].words),
                                            'room': room,
                                            'score': game_data[room].score})
        word = game_data[room].words[-1]
        data['word'] = word
        socketio.emit('set_next_word', data)
    else:
        pass
