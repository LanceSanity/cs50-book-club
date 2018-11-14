import os
import requests

from config import Config
from datetime import date
from flask import Flask, flash, render_template, redirect, session, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_session import Session
from forms import *
from functools import wraps
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)

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
            flash('Login required to write a review')
            return redirect(url_for('login'))
    return wrap

def create_app(config_class=Config):
    # ...
    if not app.debug and not app.testing:
        # ...

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/cs50-book-club.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('cs50-book-club startup')

    return app

def review_counts(isbn):
    url = 'https://www.goodreads.com/book/review_counts.json'
    payload = {'isbns': isbn}
    r = requests.get(url, params=payload)
    r_dict = r.json()['books'][0]
    return r_dict

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
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

@app.route('/search')
def search():
    q = request.args.get('q')
    search_query = '%' + q + '%'
    proxy = db.execute(("SELECT * FROM books WHERE title ILIKE (:q)"
    " OR isbn LIKE (:q) OR author ILIKE (:q)"), {'q': search_query})
    data = proxy.fetchall()
    return render_template('search.html', results=data)

@app.route('/books/<string:isbn>')
def books(isbn):
    data = db.execute('SELECT * FROM books WHERE isbn = (:isbn)',
            {'isbn': isbn}).fetchall()
    review_proxy = db.execute(('SELECT review, rating, review_date, username'
        ' FROM reviews WHERE book_id = (:isbn)'), {'isbn': isbn})
    reviews = review_proxy.fetchall()
    username = session.get('username', 'Anon')
    reviewed_query = db.execute(('SELECT review FROM reviews'
        ' WHERE username = (:username) AND book_id = (:isbn)'),
        {'username': username, 'isbn': isbn}).fetchall()
    REVIEWED_FLAG = False
    if reviewed_query:
        REVIEWED_FLAG = True
    return render_template('books.html', book=data[0], reviews=reviews,
            reviewed=REVIEWED_FLAG, review_nums=review_counts(isbn))

@app.route('/review', methods=['GET', 'POST'])
@login_required
def review():
    title = request.args.get('title', None)
    author = request.args.get('author', None)
    if request.method == 'POST':
        username = session.get('username', 'Anon')
        isbn = request.args.get('isbn', None)
        text = request.form.get('review')
        rating = request.form.get('rate')
        today = date.today()
        db.execute(('INSERT INTO reviews (review, rating, review_date,'
            ' book_id, username) VALUES (:text, :rating, :today, :isbn,'
            ' :username)'), {'text': text, 'rating': rating, 'today': today,
                'isbn': isbn, 'username': username})
        db.commit()
        flash('Review posted for {}'.format(title))
        return redirect(url_for('books', isbn=isbn))
    return render_template('review.html', title=title, author=author)

@app.route('/api/<isbn>')
def api(isbn):
    data = db.execute(('SELECT title, author, year FROM books'
        ' WHERE isbn = (:isbn)'), {'isbn': isbn}).fetchall()
    if not data:
        return jsonify({'error': 'Not found'}), 404
    d = review_counts(isbn)
    return jsonify(title=data[0][0], author=data[0][1], year=data[0][2],
            review_count=d['reviews_count'], average_score=d['average_rating'])
