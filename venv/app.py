from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify, make_response
from flask_session import Session
from tables import delete_tables, seed_tables, create_tables
from tempfile import mkdtemp
from tools import api_data, check_email, get_lemmas, login_required, get_today_formatted
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os
import requests
import sqlite3
import datetime


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

seeding = False

if seeding == True:
    delete_tables(cur)
    create_tables(cur)
    seed_tables(cur)

# Saving changes on database
con.commit()
# Closing database connection
con.close()


@app.route("/", methods=['GET'])
def index():
    user = session.get('user_id', 'not_found')
    return render_template('index.html')
        


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
            return redirect(url_for("user_progress"))


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
            new_user_id = cur.fetchone()[0]
            print(new_user_id)
            session["user_id"] = new_user_id

            flash(f"You have been successfully signed up as {name}")
            return redirect(url_for("user_progress"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/user-progress")
def user_progress():
    user_id = session.get("user_id")
    print(user_id)
    # collecting every definitions saved for the user
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()

        # check if the users has any definition saved
        cur.execute("SELECT definition_id FROM users_definitions WHERE user_id = (?)", (user_id,))
        user_has_words = cur.fetchone()
        
        # getting all words learned to calculate the number of words learned by each period (7 days, 30 days, total)
        today = datetime.datetime.today()
        progress = {
            'last7' : 0,
            'last30' : 0,
            'total' : 0
        }
        cur.execute("SELECT learned FROM users_definitions WHERE user_id = (?) AND NOT learned IS NULL", (user_id,))
        dates_learned = cur.fetchall()
        # if the user has words learned we should saved them into the progress dictionary
        if dates_learned != None:
            for date in dates_learned:
                # definition should be a date time object (it is stored as a string)
                date_learned = datetime.datetime.strptime(date[0], "%d-%m-%Y")
                # delta will be the difference between days (today and each date)
                delta = today - date_learned
                if delta.days < 7:
                    progress['last7'] += 1
                if delta.days < 30:
                    progress['last30'] += 1
            
            progress['total'] = len(dates_learned)

        if user_has_words == None:
            definitions_saved = None
            return render_template("user_progress.html", definitions=definitions_saved, progress=progress)

        else:
            cur.execute(
                '''SELECT name, definitions.definition_id, word, category, definition , example, date, learned
                    FROM definitions
                    INNER JOIN users_definitions ON users_definitions.definition_id = definitions.definition_id
                    INNER JOIN users ON  users.user_id = users_definitions.user_id
                    INNER JOIN lexical_category ON lexical_category.category_id = definitions.category_id
                    INNER JOIN words ON words.word_id = definitions.word_id
                    LEFT JOIN examples ON examples.definition_id = definitions.definition_id
                    WHERE users.user_id = (?)
                    ORDER BY learned DESC,  date DESC, words.word DESC''', (user_id,))

            words_saved = cur.fetchall()
            # saving  colums names 
            columns = [column[0] for column in cur.description]

            words = []

            for row in words_saved:
                words.append(dict(zip(columns, row)))

            # We'll save the words in a dictionary of dicts (each dict will be a word with the information)
            definitions_saved = {}

            for i in words:
                if i['definition_id'] in definitions_saved:
                    definitions_saved[i['definition_id']]['example'].append(i['example'])
                else:
                    definitions_saved[i['definition_id']] = {
                        'word': i['word'],
                        'category': i['category'],
                        'definition': i['definition'],
                        'example': [i['example']],
                        'date': i['date'],
                        'learned': i['learned']
                    }
            
            print(definitions_saved)
            return render_template("user_progress.html", definitions=definitions_saved, progress=progress)

@app.route("/navbar")
def navbar():
    return render_template("navbar.html")


@app.route("/save-word", methods=["POST"])
@login_required
def save_word():
    req = request.get_json()
    print(req)
    today = get_today_formatted()
    if 'user_id' in session:
        user = session.get('user_id')
        print(user)
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        # checking if the definition already exists in the table (we don't need to check word and category, definitions are unique)
        cur.execute("SELECT definition_id, definition FROM definitions WHERE definition=(?)", (req["definition"],))
        definition = cur.fetchone()
        
        # If the definition exists
        if definition != None:
            # checking if the user has that definition saved
            cur.execute("SELECT definition_id FROM users_definitions WHERE user_id = (?) AND definition_id = (?)", (user, definition[0]))
            definition_is_saved = cur.fetchone()
            # if the user has that definition saved, we inform him
            if definition_is_saved != None:
                response = jsonify({'message':'The word is already saved'})
                return response
            # if the user has not saved it yet, we only should assign it to the user 
            else:
                cur.execute("INSERT INTO users_definitions(user_id, definition_id, date) VALUES (?,?,?)", (user, definition[0], today))
        # if not exists, we should create it and then assign it to the user 
        else:
            # if the word doesn't exists, we should create it and save it in the table
            cur.execute("SELECT word FROM words WHERE word=(?)",(req["word"],))
            word_exists = cur.fetchone()
            if word_exists == None:
                cur.execute('INSERT INTO words (word) VALUES (?)', (req['word'],))
                new_word_id = cur.lastrowid
            # We can save the word_id as a global variable to use it onwards
            cur.execute("SELECT word_id FROM words WHERE word = (?)", (req["word"],))
            word_id = cur.fetchone()[0]

            # now we know it exists, so we should check if the lexical category chosen by the user is linked to this word, the user could
            # add more than one categories for the same word (noun, verb...) 

            # checking if the lexical category exist in the table
            cur.execute("SELECT * FROM lexical_category WHERE category = (?)", (req['lexical_category'],))
            category_exists = cur.fetchone()
            if category_exists != None:
                # checking if the word has this category linked to it
                cur.execute("SELECT * FROM definitions WHERE word_id=(?) AND category_id=(?)", (word_id, category_exists[0]))
                word_category_linked = cur.fetchone()
                # if they are not linked (any result returned), we link it
                if word_category_linked == None:
                    cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (word_id, category_exists[0]))
                # in case they are linked, we should add the new definition and its examples to this word-category (screen-noun)
                cur.execute("INSERT INTO definitions(word_id, category_id, definition) VALUES (?,?,?)",(word_id, category_exists[0], req["definition"],))
                new_definition_id = cur.lastrowid
                # inserting the examples related to the new definition
                for example in req["examples"]:
                    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (new_definition_id, example))
                # finally, linking the new definition to the user
                cur.execute("INSERT INTO users_definitions(user_id, definition_id, date) VALUES (?,?,?)", (user, new_definition_id, today))
            
            # if the category doesn't exist, we should save it first
            else:
                cur.execute('INSERT INTO lexical_category (category) VALUES (?)', (req['lexical_category'],))
                new_category_id = cur.lastrowid
                # linking the word to the new category
                cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (word_id, new_category_id))
                # Now the new category is linked to the word, we should add the definition and the examples
                cur.execute("INSERT INTO definitions(word_id, category_id, definition) VALUES (?,?,?)",(word_id, new_category_id, req["definition"]))
                new_definition_id = cur.lastrowid
                # inserting the examples related to the new definition
                for example in req["examples"]:
                    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (new_definition_id, example))
                # finally, linking the new definition to the user
                cur.execute("INSERT INTO users_definitions(user_id, definition_id, date) VALUES (?,?,?)", (user, new_definition_id, today))

        con.commit()
    response = make_response(jsonify({'message':'OK'}), 200)
    return response


@app.route("/dictionary", methods=["GET"])
def search_word():
    try:
        word = request.args.get('word')
        data = api_data(word)
        lemmas = get_lemmas(word)
        if not isinstance(lemmas, list):
            flash(lemmas)
            return redirect(url_for("index"))
        if not isinstance(data,list):
            flash(data)
            return redirect(url_for("index"))
        counter = 0
        return render_template('results.html', word=word, data=data, lemmas=lemmas, counter = counter)
    except AssertionError as error:
        return(f"{error}")


@app.route("/your-list", methods=["GET"])
def your_list():
    user_id = session.get("user_id", None)
    # collecting every definitions saved for the user
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()

        # check if the users has any definition saved
        cur.execute("SELECT definition_id FROM users_definitions WHERE user_id = (?)", (user_id,))
        user_has_words = cur.fetchone()
        if user_has_words == None:
            flash("You don't have any word saved!")
            return redirect(url_for("index"))

        cur.execute(
            '''SELECT name, definitions.definition_id, word, category, definition , example, date, learned
                FROM definitions
                INNER JOIN users_definitions ON users_definitions.definition_id = definitions.definition_id
                INNER JOIN users ON  users.user_id = users_definitions.user_id
                INNER JOIN lexical_category ON lexical_category.category_id = definitions.category_id
                INNER JOIN words ON words.word_id = definitions.word_id
                LEFT JOIN examples ON examples.definition_id = definitions.definition_id
                WHERE users.user_id = (?)
                ORDER BY learned DESC,  date DESC, words.word DESC''', (user_id,))

        words_saved = cur.fetchall()
        # saving  colums names 
        columns = [column[0] for column in cur.description]

        words = []
        # dict = {}

        for row in words_saved:
            words.append(dict(zip(columns, row)))

        # We'll save the words in a dictionary of dicts (each dict will be a word with the information)
        definitions_saved = {
            # definition_id : {
            #     word : 'word',
            #     definition : 'definition',
            #     category : 'category',
            #     examples : []
            # },
            # definition_id_2 : {
            #     word : 'word',
            #     definition : 'definition',
            #     category : 'category',
            #     examples : []
            # }
        }
        

        for i in words:
            if i['definition_id'] in definitions_saved:
                definitions_saved[i['definition_id']]['example'].append(i['example'])
            else:
                definitions_saved[i['definition_id']] = {
                    'word': i['word'],
                    'category': i['category'],
                    'definition': i['definition'],
                    'example': [i['example']],
                    'date': i['date'],
                    'learned': i['learned']
                }
        
        print(definitions_saved)

        number_of_words_learned = {
            'learned': 0,
            'unlearned': 0
        }
        # create a variable to know if there is at least one word to learn

        for id in definitions_saved:
            if definitions_saved[id]['learned'] != None:
                number_of_words_learned['learned'] += 1
            else:
                number_of_words_learned['unlearned'] += 1

        

    return render_template("words_list.html", definitions=definitions_saved, learned_counter=number_of_words_learned)


@app.route("/test")
def test():
    return render_template("test.html")


@app.route("/get-words-unlearned", methods=["GET"])
def get_words_unlearned():
    if request.method == "GET":
        user_id = session.get("user_id", None)
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()

            cur.execute(
                '''SELECT name, definitions.definition_id, word, category, definition , example, date, learned
                    FROM definitions
                    INNER JOIN users_definitions ON users_definitions.definition_id = definitions.definition_id
                    INNER JOIN users ON  users.user_id = users_definitions.user_id
                    INNER JOIN lexical_category ON lexical_category.category_id = definitions.category_id
                    INNER JOIN words ON words.word_id = definitions.word_id
                    LEFT JOIN examples ON examples.definition_id = definitions.definition_id
                    WHERE users.user_id = (?) AND learned IS NULL
                    ORDER BY learned DESC,  date DESC, words.word DESC''', (user_id, ))

            words_saved = cur.fetchall()
            # saving  colums names 
            columns = [column[0] for column in cur.description]

            words = []

            for row in words_saved:
                words.append(dict(zip(columns, row)))

            # Saving the definition in a dictionary
            words_not_learned = {}

            for i in words:
                if i['definition_id'] in words_not_learned:
                    words_not_learned[i['definition_id']]['example'].append(i['example'])
                else:
                    words_not_learned[i['definition_id']] = {
                        'word': i['word'],
                        'category': i['category'],
                        'definition': i['definition'],
                        'example': [i['example']],
                        'date': i['date'],
                        'learned': i['learned']
                    }
            print(words_not_learned)
            return jsonify(words_not_learned)



@app.route("/save-test-result", methods=["POST"])
def save_test_result():
    if request.method == 'POST':
        test_results = request.get_json()
        print(test_results)
        user_id = session.get('user_id')
        today = get_today_formatted()
        with sqlite3.connect('users.db') as con:
            cur = con.cursor()
            # changing the words unlearned to learned
            for learned_id in test_results['learned']:
                cur.execute("UPDATE users_definitions SET learned = (?) WHERE definition_id = (?) AND user_id = (?)",(today, learned_id, user_id))

            con.commit()
            response = make_response(jsonify({'message':'Results saved properly'}), 200)
            return response


@app.route("/get_user_session")
def user_session():
    user_id = session.get("user_id")
    if user_id != None:
        user = 'logged'
    else:
        user = user_id
    status = jsonify({'status': user})
    return status