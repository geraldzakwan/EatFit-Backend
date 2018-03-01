import os
import sys

from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, abort, session, redirect, render_template, jsonify

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
    try:
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
    except:
        return jsonify(
            result='false'
        )

@app.route('/signup', methods = ['POST'])
def signup():
    # try:
        signup_dictionary = {}

        signup_dictionary['username'] = request.form['username']
        signup_dictionary['email'] = request.form['email']
        signup_dictionary['password'] = request.form['password']
        signup_dictionary['height'] = request.form['height']
        signup_dictionary['weight'] = request.form['weight']
        signup_dictionary['birth_date'] = request.form['birth_date']
        signup_dictionary['gender'] = request.form['gender']
        signup_dictionary['goal'] = request.form['goal']

        # if('username' in request.form):
        #     signup_dictionary['username'] = request.form['username']
        # else:
        #     return 'Missing parameter - username'
        #
        # if('email' in request.form):
        #     signup_dictionary['email'] = request.form['email']
        # else:
        #     return 'Missing parameter - email'
        #
        # if('password' in request.form):
        #     signup_dictionary['password'] = request.form['password']
        # else:
        #     return 'Missing parameter - password'

        return db.insert_user(signup_dictionary)
    # except:
    #     return jsonify(
    #         result='false'
    #     )

# TODO : replace hardcoded path with binary image file from POST form
@app.route('/tag', methods = ['POST'])
def tag():
    # try:
        from azure.cognitiveservices.vision.customvision.prediction import prediction_endpoint
        from azure.cognitiveservices.vision.customvision.prediction.prediction_endpoint import models

        # Now there is a trained endpoint, it can be used to make a prediction

        prediction_key = os.environ['OLD_CUSTOM_VISION_PREDICTION_KEY']

        predictor = prediction_endpoint.PredictionEndpoint(prediction_key)

        # test_img_url = "http://efoodrecipe.com/wp-content/uploads/2017/01/pempek-recipes.jpg"
        # results = predictor.predict_image_url("713bf156-aae0-4994-91aa-cc565185421d", "ae152805-1e2c-46fe-a6db-a57a032d2177", url=test_img_url)

        # Alternatively, if the images were on disk in a folder called Images along side the sample.py then
        # they could be added by the following.
        #
        # Open the sample image and get back the prediction results.
        with open("image/nasi_goreng.jpg", mode="rb") as test_data:
            results = predictor.predict_image(os.environ['OLD_CUSTOM_VISION_PROJECT_ID'], test_data.read(), os.environ['OLD_CUSTOM_VISION_ITERATION_ID'])

        prediction_array = []
        prediction_json = {}
        max_probability = 0
        max_tag = 'None'

        # Display the results.
        for prediction in results.predictions:
            # print ("\t" + prediction.tag + ": {0:.2f}%".format(prediction.probability * 100))
            # prediction_json['tag'] = prediction.tag
            # prediction_json['probability'] = round(prediction.probability * 100, 2)
            # prediction_array.append(prediction_json)

            if(prediction.probability > max_probability):
                max_probability = prediction.probability
                max_tag = prediction.tag

        # Return only one tag
        return jsonify(
            result='true',
            prediction_tag=max_tag,
            prediction_probability=round(max_probability * 100, 2)
        )

        # Return all tag with each possibility value
        # return jsonify(
        #     result='true',
        #     prediction_array=json.dumps(prediction_array)
        # )
    # except:
    #     return jsonify(
    #         result='false'
    #     )

@app.route('/profile', methods = ['GET','POST'])
def profile():
    try:
        if(request.method == 'GET'):
            return db.get_user_profile(request.args.get('username'))
        elif(request.method == 'POST'):
            profile_dictionary = {}
            profile_dictionary['username'] = request.form['username']
            profile_dictionary['email'] = request.form['email']
            profile_dictionary['password'] = request.form['password']
            profile_dictionary['height'] = request.form['height']
            profile_dictionary['weight'] = request.form['weight']
            profile_dictionary['birth_date'] = request.form['birth_date']
            profile_dictionary['gender'] = request.form['gender']
            profile_dictionary['goal'] = request.form['goal']
            return db.update_user_profile(profile_dictionary)
    except:
        return jsonify(
            result='false'
        )

@app.route('/activity', methods = ['GET', 'POST'])
def activity():
    try:
        if(request.method == 'POST'):
            activity_dictionary = {}
            activity_dictionary['username'] = request.form['username']
            activity_dictionary['calory_type'] = request.form['calory_type']
            activity_dictionary['calory_amount'] = request.form['calory_amount']
            activity_dictionary['activity_name'] = request.form['activity_name']
            activity_dictionary['activity_start_hour'] = request.form['activity_start_hour']
            activity_dictionary['activity_end_hour'] = request.form['activity_end_hour']
            activity_dictionary['activity_date'] = request.form['activity_date']
            return db.insert_activity(activity_dictionary)
        elif(request.method == 'GET'):
            return db.get_activity_by_date(request.args.get('username'), request.args.get('date'))
    except:
        return jsonify(
            result='false'
        )

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
