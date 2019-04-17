# Book Club

CS50 project 1: a website with a database of books. Users can rate and write a review.

Check out the website: [link](https://cs50-book-club.herokuapp.com/)

You can also use the API route to fetch data given an ISBN: ```cs50-book-club.herokuapp.com/api/<isbn>```

Example: go to [https://cs50-book-club.herokuapp.com/api/0060929871](https://cs50-book-club.herokuapp.com/api/0060929871) for information on "A Brave New World."

### Languages/Tools/Frameworks

- Python3, HTML, CSS
- Flask microframework with a bunch of Flask extensions
- SQLAlchemy to execute SQL code. Didn't use ORM because it's too easy (and it's a project requirement)
- Bootstrap, because design takes me forever. Mad respect to front-end devs
- Gunicorn HTTP webserver (recommended by Heroku)

### How to run
1. ```git clone https://github.com/LanceSanity/cs50-book-club```
2. ```pip3 install requirements.txt```
3. Set up a SQL db (I used PostgreSQL) and run ```python3 create.py``` and ```python3 import.py```
4. ```export FLASK_APP=application.py``` and ```export DATABASE_URL= #URI of your database```
5. ```flask run```
