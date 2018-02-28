import os
import sys

from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, abort, session, redirect, render_template

from urllib import parse, request as req
from postgresql import PostgreSQL
import jwt, json

load_dotenv(find_dotenv(), override=True)

app = Flask(__name__)
db = PostgreSQL()

@app.route('/')

@app.route('/index', methods = ['GET'])
def index():
    return 'Chill~~~, jemput aku di kos dong'

@app.route('/login', methods = ['POST'])
def login():
    login_dictionary = {}

    if('password' in request.form):
        login_dictionary['password'] = request.form['password']
    else:
        return 'Missing parameter - password'

    if('username' in request.form):
        login_dictionary['username'] = request.form['username']
    elif('email' in request.form):
        login_dictionary['email'] = request.form['email']
    else:
        return 'Missing parameter - email/username'

    return db.authenticate(login_dictionary)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    try:
        port = int(os.environ['PORT'])
    except KeyError:
        print('Specify PORT as environment variable.')
        sys.exit(1)
    except TypeError:
        print('PORT must be an integer.')
        sys.exit(1)

    app.run(host='0.0.0.0', port=port, debug=True)
