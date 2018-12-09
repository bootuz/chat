from flask import render_template, flash, redirect, url_for, request
from messenger import app, db, bcrypt, socketio
from messenger.forms import RegistrationForm, LoginForm
from messenger.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import send


@app.route('/')
@app.route('/home')
def home():

    return render_template('home.html', home='HOME PAGE')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your accaunt has been created! You can now to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('chat'))
        else:
            flash('Login unsuccessful! Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', title='Chat')


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message, broadcast=True)
