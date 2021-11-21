import json
from flask import Flask, request, render_template, redirect, flash, url_for
import requests
import os
from tools import api_data, get_lemmas
from seed import seed_database, delete_tables
import sqlite3

# database connection (if the database does not exists, it creates one)
con = sqlite3.connect('users.db')

# creating a cursor to manipulate the model (database)
cur = con.cursor()

delete_tables(cur)

cur.execute(
    '''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email_address TEXT NOT NULL,
        password TEXT NOT NULL
    )'''
)

cur.execute(
    '''CREATE TABLE IF NOT EXISTS words (
        word_id INTEGER PRIMARY KEY,
        word TEXT NOT NULL
    )
    '''
)

cur.execute(
    '''CREATE TABLE IF NOT EXISTS users_words (
        users_words_id INTEGER,
        user_id INTEGER,
        word_id INTEGER,
        PRIMARY KEY(users_words_id, user_id, word_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(word_id) REFERENCES words(word_id) ON DELETE CASCADE
    )'''
)

cur.execute(
    ''' CREATE TABLE IF NOT EXISTS lexical_category (
        category_id INTEGER PRIMARY KEY,
        category TEXT
    )
    '''
)

cur.execute(
    ''' CREATE TABLE IF NOT EXISTS words_lexical_category (
        words_lexical_category_id INTEGER,
        word_id INTEGER,
        category_id INTEGER,
        PRIMARY KEY(words_lexical_category_id, word_id, category_id),
        FOREIGN KEY(word_id) REFERENCES words(word_id),
        FOREIGN KEY(category_id) REFERENCES lexical_category(category_id)
    )
    '''
)

cur.execute(
    ''' CREATE TABLE IF NOT EXISTS definitions (
        definition_id INTEGER PRIMARY KEY,
        word_id INTEGER,
        category_id INTEGER,
        definition TEXT,
        date TEXT,
        learned TEXT DEFAULT NULL,
        FOREIGN KEY(word_id) REFERENCES words(word_id),
        FOREIGN KEY(category_id) REFERENCES lexical_category(category_id)
    )
    '''
)

cur.execute(
    ''' CREATE TABLE IF NOT EXISTS examples (
        example_id INTEGER PRIMARY KEY,
        definition_id INTEGER,
        example text,
        FOREIGN KEY(definition_id) REFERENCES definitions(definition_id) ON DELETE CASCADE
    )
    '''
)

seed_database(cur)

con.commit()
con.close()


app = Flask(__name__)

app_id = os.environ['app_id']
app_key = os.environ['app_key']

app.secret_key = "myapp"




@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        try:
            word = request.form['word']
            data = api_data(word)
            lemmas = get_lemmas(word)
            if not isinstance(lemmas, list):
                flash(lemmas)
                return redirect(url_for("index"))
            return render_template('results.html', word=word, data=data, lemmas=lemmas)
        except AssertionError as error:
            return(f"{error}")


@app.route("/login", methods=['GET','POST'])
def login():
    return render_template('login.html')


@app.route("/register", methods=['GET','POST'])
def register():
    return render_template('register.html')