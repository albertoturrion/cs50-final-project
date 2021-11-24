from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_session import Session
from tables import delete_tables, seed_tables, create_tables
from tempfile import mkdtemp
from tools import api_data, check_email, get_lemmas
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os
import requests
import sqlite3



app = Flask(__name__)
app_id = os.environ['app_id']
app_key = os.environ['app_key']
app.config['SECRET_KEY'] = "7110c8ae51b3b5af97be6534caef90e4bb9bdcb3380af008f9fs43a5d1616bf319bc298105da20fe"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# database connection (if the database does not exists, it creates one)
con = sqlite3.connect('users.db')

# creating a cursor to manipulate the model (database)
cur = con.cursor()

# delete_table = False
# create_table = True
# seed_table = True


delete_tables(cur)

create_tables(cur)

seed_tables(cur)

# Saving changes on database
con.commit()
# Closing database connection
con.close()


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
            counter = 0
            return render_template('results.html', word=word, data=data, lemmas=lemmas, counter = counter)
        except AssertionError as error:
            return(f"{error}")


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # forget any user
        session.clear()

        email = request.form['email']
        password = request.form['password']
        if not email:
            flash('Please, add a valid email')
            return redirect(url_for("login"))
        
        # checking if the user exists
        with sqlite3.connect('users.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email_address = ?", (email, ))
            db_user = cur.fetchone()
            if len(db_user) == 0:
                flash("The email provided doesn't exist")
                return redirect(url_for("login"))
            if not password:
                flash("Please, enter a valid password")
                return redirect(url_for("login"))
            if not check_password_hash(db_user[3], password):
                flash("Password is not correct. Please, try again")
                return redirect(url_for("login"))
            
            # once the user has been checked should be logged in
            session['user_id'] = db_user[0]
            session['name'] = db_user[1]
            flash(f"You have been successfully logged as {db_user[1]}")
            return redirect(url_for("index"))


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        if not name:
            flash('Plase, fill your name when you register')
            return render_template('register.html')
        
        email = request.form['email']
        if not email or check_email(email) == None:
            flash('Please, enter a valid email')
            return render_template('register.html')
        # checking if name and email provided already exist
        with sqlite3.connect('users.db') as con:
            cur = con.cursor()
            cur.execute("SELECT name, email_address FROM users WHERE name=? OR email_address=?", (name, email))
            db_users = cur.fetchone()
            if not db_users == None:
                print('db_users[0]', db_users[0])
                if db_users[0].lower() == name.lower():
                    flash('Username already exists')
                    return redirect(url_for("register"))
                if db_users[1].lower() == email.lower():
                    flash('Email address already exists')
                    return redirect(url_for("register"))
            
            password = request.form['password']
            password_confirmation = request.form['password_confirmation']
            if not password or not password_confirmation:
                flash("Please, enter a valid password")
                return redirect(url_for("register"))
            if password != password_confirmation:
                flash("Make sure your password and password confirmation match")
                return redirect(url_for("register"))
            
            # Once the data provided is checked, saving the user in the table
            cur.execute("INSERT INTO users (name, email_address, password) VALUES (?,?,?)", (name, email, generate_password_hash(password, 'sha256')))
            con.commit()

            # We need the id of the user to store it in de session
            cur.execute("SELECT user_id FROM users WHERE email_address = ?", (email, ))
            new_user_id = cur.fetchone()
            print(new_user_id)
            session["user_id"] = new_user_id

            flash(f"You have been successfully signed up as {name}")
            return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/navbar")
def navbar():
    return render_template("navbar.html")