from flask import Flask, Response, request, jsonify, redirect, url_for, render_template, session, abort
import os
import pymongo
import json
from datetime import datetime
import time
seconds = time.time()

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
    # db_log.insert_one({'door': door, 'is_entry': entry(
    #     is_entry), 'time': datetime.now().timestamp()})
    new_state = update_counters(door, entry(is_entry))
    return jsonify({'status': 'saved', 'state': new_state})

@app.route("/api/log")
def log_all():
    all_log = list(db_log.find())
    for x in all_log:
        del x['_id']
    return jsonify(all_log)

@app.route("/reset")
def reset_all():
    db_log.remove({})
    state.remove({})
    return jsonify({'logs': db_log.count(), 'state': state.count() })


def update_log():
    current = state.find_one({'index': 1})
    del current['_id']
    current['time'] = time.time()
    current['hour'] = datetime.now().hour
    current['minute'] = datetime.now().minute
    current['second'] = datetime.now().second
    current['ts'] = datetime.now().strftime("%c")
    db_log.insert_one(current)


def update_counters(door, is_entry):
    current = state.find_one()
    if current is None:  # Check if document empty
        current_state = {'index': 1, 'door1_entries': 0, 'door2_entries': 0,
                         'door1_exits': 0, 'door2_exits': 0, 'people_count': 0}
        state.insert_one(current_state)
        update_log()
        print(state.find_one())

    if(door == 1):
        if is_entry:
            state.update_one(
                {'index': 1}, {'$inc': {'door1_entries': 1, 'people_count': 1}})
            update_log()
        else:
            state.update_one(
                {'index': 1}, {'$inc': {'door1_exits': 1,'people_count': -1}})
            update_log()
    elif(door == 2):
        if is_entry:
            state.update_one(
                {'index': 1}, {'$inc': {'door2_entries': 1, 'people_count': 1}})
            update_log()
        else:
            state.update_one(
                {'index': 1}, {'$inc': {'door2_exits': 1,'people_count': -1}})
            update_log()
    else:
        raise ValueError("Invalid Door Number")
    ret_val = state.find_one()
    del ret_val['_id']
    return ret_val

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
