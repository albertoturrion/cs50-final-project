# ENGLISH INMERSION
#### Video Demo:  <URL HERE>
#### Description:
English Inmersion **is a web app made for English learners** like me. 
The main objective of the site is to make easier to the user to learn English, specifically vocabulary. All the information comes from [Oxford Dictionaries API](https://developer.oxforddictionaries.com/) using the free plan.
Once the user has accessed the website, he can search for words and see its lexical categories, definitions and examples.
If the user registers on the websites, he can save definitions and learn vocabulary through tests. If the user make the test of the words saved (and not learned), **he can learn each word if he guesses the answer**.
Moreover, each user can see his learning progress, showing the words learned the last 7 days, the last 30 days and the total words learned.

##### How the webapp is made
The website is made with Flask (Python microframework), sqlite3 for database and javascript vanilla. Bootstrap is also used to style the user interface, but just for navigation bar and container.

###### Python files
- **app.py** is the main Python file. In this file you can check the routes of the website.
- **tools.py** is this Python file you can see some functions done to be imported to the main Python file. 
    - Interact with the Oxford API.
    - Check email entered by the user when register on the website.
    - Create view decorators as login_required.
    - Format the date.
- **tables.py** is made to seed the database. You can use "seeding" variable (in app.py file) to call the functions made in this file:
    - delete_tables()
    - create_tables()
    - seed_tables()


#### Setting up the environment
##### Clone the folder
`git clone https://github.com/albertoturrion/cs50-final-project.git`

Out of the ***englishInmersion*** folder:

##### Create the enviroment
Mac: `python3 -m venv venv` Windows: `py -3 -m venv venv`

##### Activate virtual environment
In the folder which contains the venv file:
Mac: `source venv/bin/activate` Windows (Bash): `source venv\Scripts\activate`

##### Install modules
Make sure virtual enviroment is activated
`pip install -r requirements.txt`

##### Export variables
You can get your Oxford Dictionaries API credentials signing up on [Oxford Dictionaries API plans](https://developer.oxforddictionaries.com/?tag=#plans)
`export FLASK_APP=englishInmersion/app.py`
`export app_id={{ your app_id }}` 
'export app_key={{ your app_key }}` 
`export FLASK_ENV=development`

##### Finally, run the project
`flask run`

##### Deactivate virtual environment
`deactivate`



