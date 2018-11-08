import os

from flask import Flask, flash, render_template, redirect, session, url_for, request
from flask_session import Session
from forms import *
from functools import wraps
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'secret, lol'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Helper methods
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login required')
            return redirect(url_for('login'))
    return wrap

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
#        flash('Login requested for user {}, remember_me={}'.format(
#            form.username.data, form.remember_me.data))
        username = form.username.data
        proxy = db.execute('SELECT * FROM users WHERE username = (:username)',
                {'username': username})
        data = proxy.fetchall()
        if not data:
            flash('Username: {} does not exist.'.format(username))
            return render_template('login.html', title='Sign In', form=form)
        if sha256_crypt.verify(request.form['password'], data[0][2]):
            session['logged_in'] = True
            session['username'] = form.username.data
            return redirect(url_for('index'))
        else:
            flash('Password incorrect, try again.')
            return render_template('login.html', title='Sign In', form=form)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have successfully logged out.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt((str(form.password.data)))
        r = db.execute('SELECT username FROM users WHERE username = (:username)',
                {'username': username})
        r2 = db.execute('SELECT email FROM users WHERE email = (:email)',
                {'email': email})
        if r.fetchall():
            flash('That username has been taken, please try another.')
            return render_template('register.html', title='Register', form=form)
        elif r2.fetchall():
            flash('That email address has already been registered.')
            return render_template('register.html', title='Register', form=form)
        else:
            db.execute(('INSERT INTO users (username, password_hash, email)'
                ' VALUES (:username, :password, :email)'),
                {'username': username, 'password': password, 'email': email})
            db.commit()
            flash('Thanks for registering!')
            return render_template('index.html')
    return render_template('register.html', form=form)
