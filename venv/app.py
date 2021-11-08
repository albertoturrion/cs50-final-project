import json
from flask import Flask, request, render_template
import requests
import os
from tools import api_data


app = Flask(__name__)

app_id = os.environ['app_id']
app_key = os.environ['app_key']
# print(app_id)
# print(app_key)

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('hello.html')
    else:
        try:
            word = request.form['word']
            data = api_data(word)
            return render_template('results.html', word=word, data=data)
        except AssertionError as error:
            return(f"{error}")
    