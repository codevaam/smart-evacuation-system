from flask import Flask, Response, request, jsonify, redirect, url_for, render_template, session, abort
import os
import pymongo
import json
from datetime import datetime


client = pymongo.MongoClient('db', 27017)
db = client['db1']

state = db['state']
db_log = db['db_log']


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://db:27017/db1"
app.config['SECRET_KEY'] = 'secret!'

# Sanity Check
@app.route("/ping")
def ping():
    app.logger.info("Responded ping with pong")
    return "Pong"


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/log/<int:door>/<int:is_entry>")
def log_event(door, is_entry):
    def entry(x): return x == 1
    db_log.insert_one({'door': door, 'is_entry': entry(
        is_entry), 'time': datetime.now().timestamp()})
    new_state = update_counters(door, is_entry)
    return jsonify({'status': 'saved', 'state': new_state})


def update_counters(door, is_entry):
    current = state.find_one()
    if len(current) == 0:  # Check if document empty
        state.insert_one({'door1_entries': 0, 'door2_entries': 0,
                          'door1_exits': 0, 'door2_exits': 0, 'people_count': 0})
    if(door == 1):
        if is_entry:
            pass
        else:
            pass
        pass
    elif door == 2:
        pass
    else:
        raise ValueError("Invalid Door Number")
    return {}

# @app.route("/upload/temperature/<float:temp>/<float:hum>")
# def temp_upload(temp,hum):
#     tmp.update_one({'time':datetime.now().hour},{'$set': {'temperature': temp, 'humidity': hum}}, upsert=False)
#     return jsonify({'status': 'saved'})


# @app.route("/get/temperature/current")
# def temp_get_current():
#     data = tmp.find_one({'time':datetime.now().hour })
#     return str(data['temperature'])

# @app.route("/upload/water_level/<float:level>/")
# def level_upload(level):
#     levels.update_one({'time':datetime.now().hour},{'$set': {'level': level}}, upsert=False)
#     return jsonify({'status': 'saved'})


if __name__ == "__main__":
    Flask.run(app, host='0.0.0.0', port=5000, debug=True)
