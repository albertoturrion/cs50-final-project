from werkzeug.security import check_password_hash, generate_password_hash

def create_tables(cur):
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


def delete_tables(cur):
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS words")
    cur.execute("DROP TABLE IF EXISTS users_words")
    cur.execute("DROP TABLE IF EXISTS lexical_category")
    cur.execute("DROP TABLE IF EXISTS words_lexical_category")
    cur.execute("DROP TABLE IF EXISTS words_lexical_category")
    cur.execute("DROP TABLE IF EXISTS definitions")
    cur.execute("DROP TABLE IF EXISTS examples")


# this module is used to seed the database (add initial values)
def seed_tables(cur):
    
    password1 = generate_password_hash('Alberto123','sha256')
    password2 = generate_password_hash('Juan123','sha256')

    # seed users table
    users = [
        {
            'name':'Alberto',
            'email_adress': 'alberto@gmail.com',
            'password': password1
        },
        {
            'name':'Juan',
            'email_adress': 'juan@gmail.com',
            'password': password2
        }
    ]

    # seed users table
    for user in users:
        cur.execute("INSERT INTO users(name, email_address, password) VALUES (?,?,?)",(user['name'],user['email_adress'],user['password']))

    # seed words table
    words = ['granted', 'screen', 'television', 'developer']
    for word_example in words:
        cur.execute("INSERT INTO words (word) VALUES (?)", (word_example,))

    # seed users_words
    cur.execute("INSERT INTO users_words VALUES (?,?,?)", (1,1,1))
    cur.execute("INSERT INTO users_words VALUES (?,?,?)", (1,1,2))
    cur.execute("INSERT INTO users_words VALUES (?,?,?)", (1,1,4))
    cur.execute("INSERT INTO users_words VALUES (?,?,?)", (1,2,3))
    cur.execute("INSERT INTO users_words VALUES (?,?,?)", (1,2,4))

    # seed lexical_category table
    lexical_categories = ['noun', 'verb', 'conjunction', 'adjective','adverb']
    for category in lexical_categories: 
        cur.execute("INSERT INTO lexical_category (category) VALUES (?)", (category,))

    # seed words_lexical_category table
    cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (1,4))
    cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (1,2))
    cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (2,1))
    cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (2,2))
    cur.execute("INSERT INTO words_lexical_category(word_id, category_id) VALUES (?,?)", (2,1))

    # seed definitions table

    dates = ["2021-04-10","2021-06-09","2021-02-03","2021-06-13","2021-08-23","2021-11-10"]
    
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (1,5,"admittedly; it is true (used to introduce a factor which is opposed to the main line of argument but is not regarded as so strong as to invalidate it","2021-02-03",None))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (1,3,"even assuming that","2021-03-03","2021-03-07"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,1,"a fixed or movable upright partition used to divide a room, give shelter from drafts, heat, or light, or to provide concealment or privacy","2021-04-10","2021-04-23"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,1,"a flat panel or area on an electronic device such as a television, computer, or smartphone, on which images and data are displayed","2021-05-03","2021-05-07"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,1,"a transparent, finely ruled plate or film used in halftone reproduction.","2021-10-09","2021-10-18"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,1,"a detachment of troops or ships detailed to cover the movements of the main body","2021-03-03", None))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,1,"a large sieve or riddle, especially one for sorting substances such as grain or coal into different sizes","2021-01-02","2021-01-04"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,2,"conceal, protect, or shelter (someone or something) with a screen or something forming a screen","2021-11-03","2021-11-17"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,2,"show (a movie or video) or broadcast (a television program)","2021-02-03","2021-02-18"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,2,"test (a person or substance) for the presence or absence of a disease or contaminant","2021-02-03","2021-02-18"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,2,"pass (a substance such as grain or coal) through a large sieve or screen, especially so as to sort it into different sizes","2021-06-15","2021-06-18"))
    cur.execute("INSERT INTO definitions (word_id, category_id, definition, date, learned) VALUES (?,?,?,?,?)", (2,2,"project (a photograph or other image) through a transparent ruled plate so as to be able to reproduce it as a halftone.","2021-07-24", None))

    # seed examples table
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (1, "granted, sitting around the house may not be your idea of the perfect retirement, but what's your choice when inflation is eroding the value of your nest egg?"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (2, "granted that officers were used to making decisions, they still couldn't be expected to understand"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (3, "a room with a red carpet and screens with oriental decorations"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (4, "a television screen"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (6, "HMS Prince Leopold and HMS Prince Charles sailed for Shetland with a screen of four destroyers"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (7, "the material retained on each sieve screen is weighed in turn"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (8, "her hair swung across to screen her face"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (8, "a high hedge screened all of the front from passersby"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (9, "the show is to be screened by HBO later this year"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (10, "outpatients were screened for cervical cancer"))
    cur.execute("INSERT INTO examples (definition_id, example) VALUES (?,?)", (11, "granulated asphalt—manufactured to 40 mm down or screened to 28 mm & 14 mm down"))