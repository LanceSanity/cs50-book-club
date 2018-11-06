import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_tables():
    """Creates books, users, and reviews tables"""
    commands = (
        ('CREATE TABLE books ('
            'isbn VARCHAR PRIMARY KEY, '
            'title VARCHAR NOT NULL, '
            'author VARCHAR NOT NULL, '
            'year SMALLINT NOT NULL)'),
        ('CREATE TABLE users ('
            'id SERIAL PRIMARY KEY, '
            'email VARCHAR NOT NULL, '
            'password_hash VARCHAR NOT NULL, '
            'username VARCHAR NOT NULL) '),
        ('CREATE TABLE reviews ('
            'review_id SERIAL PRIMARY KEY, '
            'review VARCHAR NOT NULL, '
            'rating SMALLINT NOT NULL, '
            'book_id VARCHAR, FOREIGN KEY(book_id) REFERENCES books(isbn), '
            'user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))')
        )
    for command in commands:
        db.execute(command)
    db.commit()

if __name__ == '__main__':
    create_tables()
