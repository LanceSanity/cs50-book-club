import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_tables():
    """Add tables to db"""
    commands = (
            """
            CREATE TABLE books (
                isbn PRIMARY KEY,
                title VARCHAR NOT NULL,
                author VARCHAR NOT NULL,
                year YEAR(4) NOT NULL
            )
            """,
            """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR NOT NULL
            )
            """,
            """
            CREATE TABLE reviews (
                review_id SERIAL PRIMARY KEY,
                
            
            )
            """)

def main():
    """import books in PostgreSQL db"""
    with open('books.csv') as f:
        reader = csv.reader(f)
