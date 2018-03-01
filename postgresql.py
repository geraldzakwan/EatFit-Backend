import os
import sqlalchemy
import json

from flask import jsonify
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import or_, func

load_dotenv(find_dotenv(), override=True)

class PostgreSQL:
    # Sample use
    # from postgresql import PostgreSQL
    # db = PostgreSQL()
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

    # Insert

    # Sample use
    # db.insert_food_calory({
    #     'food_name' : 'Nasi Goreng',
    #     'calory_amount' : 250
    # })
    # TODO : check if username already exists
    def insert_user(self, user_dictionary):
        clause = self.users_table.insert().values(user_dictionary)
        self.con.execute(clause)
        user_json = json.dumps(user_dictionary)
        return jsonify (
            return='true',
            user=user_json
        )

    # Sample use
    # db.insert_food_calory({
    #     'username' : 'geraldzakwan',
    #     'email' : 'geraldi.dzakwan@gmail.com',
    #     'password' : 'lerpekadutanjing',
    # })
    def insert_food_calory(self, food_calory_dictionary):
        clause = self.food_calories_table.insert().values(food_calory_dictionary)
        self.con.execute(clause)

    # Sample use
    # db.batch_insert_food_calories('List Makanan.csv')
    # Csv header : no, food_meal, calory_amount
    def batch_insert_food_calories(self, csv_path):
        csv_dataframe = pd.read_csv(csv_path)

        for index, series in csv_dataframe.iterrows():
            food_calory_dict = {}
            for elem in series.iteritems():
                if(elem[0] != 'no'):
                    food_calory_dict[elem[0]] = elem[1]
            self.insert_food_calory(food_calory_dict)

    # Login sample use
    # db.authenticate {
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
                return='true',
                status='true',
                user=user_json
            )
        else:
            return jsonify(
                return='true',
                status='false'
            )

    # Get user info
    def get_user_profile(self, username):
        clause = self.users_table.select().where(
            self.users_table.c.username == username
        )
        user = self.con.execute(clause).fetchone()

        user_json = json.dumps(user.items())
        return jsonify(
            'return':'true',
            user=user_json
        )

    # Update user info
    def update_user_profile(self, username, profile_dictionary):
         clause = self.users_table.update().where(
                    self.users_table.c.username==username
                  ).values(
                    username=profile_dictionary['username'],
                    email=profile_dictionary['email'],
                    password=profile_dictionary['password'],
                    height=profile_dictionary['height'],
                    weight=profile_dictionary['weight'],
                    birth_date=profile_dictionary['birth_date']
                  )
        return jsonify(
            'return':'true',
            user=json.dumps(profile_dictionary)
        )
