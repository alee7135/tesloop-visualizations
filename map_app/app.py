import sys
sys.path.append("/Users/alee/Documents/Job Take Homes/")
import psycopg2
from psycopg2 import extras
import pprint
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import pandas
import numpy as np
import pprint

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/form')
def filter_date():
    date_range = request.args.get('daterange',0, type=str).split(" - ")
    query = "SELECT * FROM vehicle_data where timestamp>='%s' AND timestamp<'%s'" %(date_range[0], date_range[1])
    print query

    cursor = connect()
    cursor.execute(query)
    # cursor = [{"heading": 164, "longitude": -118.397822, "shift_state": "null", "latitude": 33.73879, "gps_as_of": 1464839751, "speed": "null"},
    # {"speed": "null", "latitude": 33.73879, "heading": 164, "gps_as_of": 1464840779, "shift_state": "null", "longitude": -118.397822}]
    point_geojson, line_geojson = create_geojson(cursor)
    pprint.pprint(line_geojson)
    return jsonify(point_geojson=point_geojson, line_geojson=line_geojson)

def create_geojson(cursor):
    point_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    line_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    line_string = [] # hold the line string
    speed = []
    for q in cursor:
        single_point = [q['drive_state']['longitude'],q['drive_state']['latitude']]
        line_string.append(single_point)
        if q['drive_state']['speed']: # if it is not None
            speed.append(q['drive_state']['speed'])
        point_geojson['features'].append(create_point_feature(q, single_point))
    line_geojson['features'].append(create_line_feature(np.mean(speed), line_string))
    return point_geojson, line_geojson

def create_point_feature(q, single_point):
    return {
        "type": "Feature",
        "properties": {"description": "<p><strong>SOC</strong><span> :  "+str(q['charge_state']['battery_level'])+"</span></p><p><strong>Range</strong><span> : "+str(q['charge_state']['battery_range'])+"</span></p>"},
        "geometry":{"type":"Point", "coordinates": single_point }
    }

def create_line_feature(avg_speed, line_string):
    return {
        "type": "Feature",
        "properties": {"speed": avg_speed},
        "geometry":{"type":"LineString", "coordinates": line_string}
    }

def connect():
    # Define connection string
    conn_string = "host='tesla-vehicle-api-db.ct6ob3lecz50.us-west-2.rds.amazonaws.com' \
                   dbname = 'tesloop' \
                   user='tesmin' \
                   password='S100pdogg!e' \
                   port = 5432"
    print "Connecting to database\n --> %s" %conn_string

    # actually make connection, if connection can't be made, then we raise exception here
    conn = psycopg2.connect(conn_string)
    # get a cursor object which we use to perform queries
    cursor = conn.cursor('cursor1', cursor_factory=psycopg2.extras.DictCursor)
    print "Successfully Connected!\n"
    return cursor


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
