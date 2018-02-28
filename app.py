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

@app.route("/index", methods=['GET', 'POST'])
def callback():
    return 'App running well'

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
