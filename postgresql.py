import os
import sqlalchemy
import json

from flask import jsonify
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import or_, func

load_dotenv(find_dotenv(), override=True)

class PostgreSQL:
    def __init__(self):
        self.con, self.meta = self._connect()
        self.food_calories_table = self.meta.tables['food_calories']
        self.activity_calories_table = self.meta.tables['activity_calories']
        self.users_table = self.meta.tables['users']

    @staticmethod
    def _connect():
        url = os.environ['AZURE_DATABASE_URL']
        con = sqlalchemy.create_engine(url, client_encoding='utf8')
        meta = sqlalchemy.MetaData(bind=con, reflect=True)

        return con, meta

    # Login sample use
    # postgres_obj.authenticate {
    #   'username' : 'geraldzakwan'
    #   'password' : 'lerpekadutanjing'
    # }
    def authenticate(self, login_dictionary):
        if('username' in login_dictionary):
            clause = self.users_table.select().where(
                self.users_table.c.username == login_dictionary['username']
            )
            user = self.con.execute(clause).fetchone()
        elif('email' in login_dictionary):
            clause = self.users_table.select().where(
                self.users_table.c.email == login_dictionary['email']
            )
            user = self.con.execute(clause).fetchone()
        else:
            return 'Authentication error - missing username/email'

        user_json = json.dumps(user.items())
        if(user['password'] == login_dictionary['password']):
            return jsonify(
                msg='Authentication succesful',
                user=user_json
            )
        else:
            return jsonify(
                msg='Authentication failed - wrong password'
            )
