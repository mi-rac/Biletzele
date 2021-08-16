from flask import render_template, flash, redirect, url_for, request
from app import app

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html')
    else:
        return redirect(url_for('home'))
