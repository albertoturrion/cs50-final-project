import datetime
import json
import os
import re
from functools import wraps

import requests
from flask import flash, redirect, render_template, request, session, url_for

app_id = os.getenv('app_id')
app_key = os.getenv('app_key')

# function to get only the api data needed to the MVP - lexical category, definitions, examples
def api_data(word):
    # Use the entries and en-us language as default
    baseEntriesURL = "https://od-api.oxforddictionaries.com/api/v2/entries/en-us/"
    # Now, we add the word searched by the user
    entriesURL = baseEntriesURL + word.lower()
    base_word = word

    # Making the request
    r = requests.get(entriesURL, headers={"app_id": app_id, "app_key": app_key})
    if r.status_code == 200:
        # Turning response into json format
        response = r.json()
        # We should access to "results" array, it contains "id" and "lexicalEntries"
        results = response["results"][0]
        # To get the definitions, we should enter to lexicalEntries, an array of dictionaries with 
        # some information about the different lexical categories of the word searched
        # For instance, grant as a noun (one dict) and as a verb (another dict)
        lexicalEntries = results["lexicalEntries"]
        # We'll save each entry of word within a dictionary (word) and each entry within an array (words) 
        # It is possible that exists more than one entry (grant as a verb and as a noun). Each of them (and their data)
        # will be in a dictionary
        words = []
        lexicalCategory = []
        for word in lexicalEntries:
            # In each entry it will be saved the information of each entry: category, definitions and examples
            # senseinformation contains the different definitions of the same lexical category and their examples
            # Each definition can have one or more examples, but there always will be the same number of elements in each array
            # However, within the examples, one element can contain severeal examples as an array
            entry = {
            'lexicalCategory': None,
            'senseInformation': {
                "definitions": [],
                "examples": []
            }
            }
            # Saving the lexical category
            entry["lexicalCategory"] = (word["lexicalCategory"]["text"])
            # we should access to "entries" to have access to definitions and examples
            entries = word["entries"]
            # each entry (verb or noun) can have more than one sense (with its definitions, pronunciations...)
            senseInformation = {
                "definitions": [],
                "examples": []
            }
            for i in entries:
                senses = i['senses']
                for sense in senses:
                    try:
                        senseInformation["definitions"].append(sense["definitions"][0])
                    except:
                        return f"Sorry, we don't have the word {base_word} in our dictionary"
                    # It's possible that some definition doesn't have examples, so we need to manage the exception
                    try: 
                        examples = sense["examples"]
                        # It's needed to add every examples of one definition in one array to know what examples was assigned to the definition
                        # they can be one or more than one
                        wordExamples = []
                        for example in examples:
                            wordExamples.append(example['text'])
                        senseInformation["examples"].append(wordExamples)
                    except:
                        senseInformation["examples"].append(['None'])
                # we save the information of the entry (verb or noun) with all its definitions and examples
                entry['senseInformation'] = senseInformation
                # adding the entry to word, it can have more than one entry
                words.append(entry)
        return words
    else:
        # if it doesn't return 200 status code and it's not catched as an error
        return (f'Sorry, the word {base_word} has not been found')


# this function return a dictionary with the different lemmas of the word searched
def get_lemmas(word):
    # Use the lemmas and en-us language as default
    baseLemmasURL = "https://od-api.oxforddictionaries.com/api/v2/lemmas/en-us/"
    # Now, we add the word searched by the user
    lemasURL = baseLemmasURL + word.lower()
    # It is possible something goes wrong when we make the requests, so we should handle the error
    try:
        r = requests.get(lemasURL, headers={'app_id': app_id, 'app_key': app_key})
    except AssertionError as error:
        flash(error)
        return redirect(url_for("index"))
    
    if r.status_code == 200:
        response = r.json()
        # accessing to lexical entries, when the relevant information is
        lexicalEntries = response['results'][0]['lexicalEntries']
        # We will save each lemma and its lexical category in a dictionary
        # It is not necessary to save the inflection because it's always the word searched
        inflections = []
        for inflect in lexicalEntries:
            inflection = {
                'lemma': None,
                'lexicalCategory': None,
            }
            inflection['lemma'] = inflect['inflectionOf'][0]['text']
            inflection['lexicalCategory'] = inflect['lexicalCategory']['text']
            
            # Save the lemma in the inflections dictionary
            inflections.append(inflection)
        
        return inflections
    else:
        # When the API doesn't return lemmas because the word typed doesn't exist, we return the error
        # of the api
        response = r.json()
        return response['error']


def check_email(email):
    regular_expression = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regular_expression, email)


# https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_today_formatted():
    today = datetime.date.today()
    # converting date to string
    today_str = today.strftime("%d-%m-%Y")
    return today_str
