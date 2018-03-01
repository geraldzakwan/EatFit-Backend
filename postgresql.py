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
            result='true',
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
            return jsonify(
                result='false',
                msg='Authentication error - missing username/email'
            )

        if(user == None):
            return jsonify(
                result='false',
                msg='Authentication error - username/email not found'
            )

        user_json = json.dumps(user.items())
        if(user['password'] == login_dictionary['password']):
            return jsonify(
                result='true',
                status='true',
                user=user_json
            )
        else:
            return jsonify(
                result='true',
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
            result='true',
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
                    birth_date=profile_dictionary['birth_date'],
                    gender=profile_dictionary['gender'],
                    goal=profile_dictionary['goal']
                  )

        return jsonify(
            result='true',
            user=json.dumps(profile_dictionary)
        )

    # Insert

    # Sample use
    # db.insert_food_calory({
    #     'food_name' : 'Nasi Goreng',
    #     'calory_amount' : 250
    # })
    # TODO : check if username already exists
    def insert_activity(self, activity_dictionary):
        clause = self.activity_calories_table.insert().values(activity_dictionary)
        self.con.execute(clause)
        activity_calory_json = json.dumps(activity_dictionary)
        return jsonify (
            result='true',
            activity_calory=activity_calory_json
        )

    # Insert

    # Sample use
    # db.insert_food_calory({
    #     'food_name' : 'Nasi Goreng',
    #     'calory_amount' : 250
    # })
    # TODO : check if username already exists
    def get_activities_by_date(self, username, date):
        clause = self.activity_calories_table.select().where(
            self.activity_calories_table.c.username == username
        ).where(
            self.activity_calories_table.c.activity_date == date
        )

        activity_calories = self.con.execute(clause).fetchall()
        activity_array = []
        for activity in activity_calories:
            activity_array.append(activity.items())

        activity_calory_json = json.dumps(activity_array)

        return jsonify (
            result='true',
            activity_calory=activity_calory_json
        )

    # Sample use
    # db.insert_food_calory({
    #     'food_name' : 'Nasi Goreng',
    #     'calory_amount' : 250
    # })
    # TODO : check if username already exists
    def get_summary_by_date(self, username, date):
        clause = self.activity_calories_table.select().where(
            self.activity_calories_table.c.username == username
        ).where(
            self.activity_calories_table.c.activity_date == date
        )

        activity_calories = self.con.execute(clause).fetchall()
        total_calories = 0

        for activity in activity_calories:
            # print(activity.items())
            if(activity['calory_type'] == '+'):
                total_calories = total_calories + activity['calory_amount']
            elif(activity['calory_type'] == '-'):
                total_calories = total_calories - activity['calory_amount']

        return jsonify (
            result='true',
            total_calories=total_calories
        )
