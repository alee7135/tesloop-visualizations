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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=['GET','POST'])
def input():
    # Takes as input the UTC time, and then I query the database with UTC
    # Return output as PDT
    start = "1452153600" #request.args.get('start_json',0, type=str)
    end = "1465282800" #request.args.get('end_json', 0, type=str)
    print 'START: ', start
    print 'END: ', end
    cursor = connect()
    # query sql at UTC but return dates in PDT
    query = """SELECT ceiling(extract(epoch from timestamp AT TIME ZONE 'PDT'))::int as timestamp_pdt, timestamp AT TIME ZONE 'PDT' AS timestamp_real,drive_state, charge_state, climate_state
            FROM vehicle_data WHERE extract(epoch from timestamp)>='%s' and extract(epoch from timestamp)<='%s' """ %(start,end)

    # select timestamp, extract(epoch from timestamp) as utc_time, timestamp at time zone 'pdt' as timestamp_pdt,
	# extract(epoch from timestamp at time zone 'pdt')

    # print query
    cursor.execute(query)
    # Lets create some variables to store the data
    batt_range = []
    est_batt_range = []
    bb_level = []
    speed = []
    charger_actual_current = []
    charger_pilot_current = []
    charger_power = []
    charger_voltage = []

    # Loop through the cursor object
    for i in cursor:

        batt_range.append([int(i['timestamp_pdt']*1000), i['charge_state']['battery_range']])
        est_batt_range.append([int(i['timestamp_pdt']*1000), i['charge_state']['est_battery_range']])
        bb_level.append([int(i['timestamp_pdt']*1000), i['charge_state']['battery_level']])

        # speed.append([int(i['timestamp_pdt']*1000),
        # i['drive_state']['speed']])
        #
        # charger_actual_current.append([int(i['timestamp_pdt']*1000),
        # i['charge_state']['charger_actual_current']])
        # charger_pilot_current.append([int(i['timestamp_pdt']*1000),
        # i['charge_state']['charger_pilot_current']])
        # charger_power.append([int(i['timestamp_pdt']*1000),
        # i['charge_state']['charger_power']])
        # charger_voltage.append([int(i['timestamp_pdt']*1000),
        # i['charge_state']['charger_voltage']])

    return jsonify(batt_range=batt_range,est_batt_range=est_batt_range,bb_level=bb_level)
            #
            # speed = speed,
            #
            # charger_actual_current = charger_actual_current,
            # charger_pilot_current = charger_pilot_current,
            # charger_power = charger_power,
            # charger_voltage = charger_voltage


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
    app.run(debug=True)
