import json
from flask import Flask, request, render_template, redirect, flash, url_for
import requests
import os
from tools import api_data, get_lemmas


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
    