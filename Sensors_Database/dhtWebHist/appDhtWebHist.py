#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  appDhtWebHist_v2.py
#  
#  Created by MJRoBot.org 
#  10Jan18

'''
	RPi WEb Server for DHT captured data with Gage and Graph plot  
'''

from datetime import datetime,timedelta

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request,jsonify
app = Flask(__name__)

import sqlite3

# Retrieve LAST data from database
def getLastData():
	conn1=sqlite3.connect('../sensorsData.db', check_same_thread=False)
	curs=conn1.cursor()
	for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		temp = row[1]
		hum = row[2]
	conn1.close()
	return time, temp, hum

# Get 'x' samples of historical data
def getHistData (numSamples):
	conn2=sqlite3.connect('../sensorsData.db', check_same_thread=False)
	curs=conn2.cursor()
	curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
	data = curs.fetchall()
	dates = []
	temps = []
	hums = []
	for row in reversed(data):
		dates.append(row[0])
		temps.append(row[1])
		hums.append(row[2])
		temps, hums = testeData(temps, hums)
	conn2.close()
	return dates, temps, hums

# Test data for cleanning possible "out of range" values
def testeData(temps, hums):
	n = len(temps)
	for i in range(0, n-1):
		if (temps[i] < -10 or temps[i] >50):
			temps[i] = temps[i-2]
		if (hums[i] < 0 or hums[i] >100):
			hums[i] = temps[i-2]
	return temps, hums


# Get Max number of rows (table size)
def maxRowsTable():
	conn3=sqlite3.connect('../sensorsData.db', check_same_thread=False)
	curs=conn3.cursor()
	for row in curs.execute("select COUNT(temp) from  DHT_data"):
		maxNumberRows=row[0]
	conn3.close()
	return maxNumberRows

# Get sample frequency in minutes
def freqSample():
	times, temps, hums = getHistData (2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(times[0], fmt)
	tstamp1 = datetime.strptime(times[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()/60))
	return (freq)

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
        numSamples = 100

global freqSamples
freqSamples = freqSample()

global rangeTime
rangeTime = 100
				
		
# main route 
@app.route("/")
def index():
	time, temp, hum = getLastData()
	templateData = {
	  'time'		: time,
          'temp'		: temp,
          'hum'			: hum,
          'freq'		: freqSamples,
          'rangeTime'		: rangeTime
	}
	return render_template('index.html', **templateData)


@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples 
    global freqSamples
    global rangeTime
    rangeTime = int (request.form['rangeTime'])
    if (rangeTime < freqSamples):
        rangeTime = freqSamples + 1
    numSamples = rangeTime//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    time, temp, hum = getLastData()
    
    templateData = {
	  'time'		: time,
          'temp'		: temp,
          'hum'			: hum,
          'freq'		: freqSamples,
          'rangeTime'	        : rangeTime
	}
    return render_template('index.html', **templateData)
	
	
@app.route('/plot/temp')
def plot_temp():
	try:
		times, temps, hums = getHistData(numSamples)
		ys = temps
		fig = Figure()
		axis = fig.add_subplot(1, 1, 1)
		axis.set_title("Temperature [oC]")
		axis.set_xlabel("Samples")
		axis.grid(True)
		xs = range(numSamples)
		axis.plot(xs, ys)
		canvas = FigureCanvas(fig)
		output = io.BytesIO()
		canvas.print_png(output)
		response = make_response(output.getvalue())
		response.mimetype = 'image/png'
		
		return response
	except Exception as e:
		print(f"An error occurred: {e}")  
		return make_response("Error generating plot", 500)

@app.route('/plot/hum')
def plot_hum():
	times, temps, hums = getHistData(numSamples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
@app.route("/plot/data")
def plot_data():
	time, temp, hum = getLastData()
	times, temps, hums = getHistData (2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(times[0], fmt)
	tstamp1 = datetime.strptime(times[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()/60))
	tData = {
	  'time'		: time,
	  'temp'		: temp,
          'hum'			: hum,
          'freq'		: freq,
          'rangeTime'		: rangeTime
	}
	return 	jsonify(tData)
@app.route('/get_data_by_minute', methods=['POST'])
def get_data_by_minute():
    exact_time_str = request.form['exact_time']
    try:
        exact_time = datetime.strptime(exact_time_str, '%Y-%m-%dT%H:%M')
        start_of_minute = exact_time
        end_of_minute = start_of_minute + timedelta(minutes=1)

        conn = sqlite3.connect('../sensorsData.db', check_same_thread=False)
        curs = conn.cursor()
        curs.execute("""
            SELECT * FROM DHT_data
            WHERE timestamp >= ? AND timestamp < ?
        """, (start_of_minute, end_of_minute))
        rows = curs.fetchall()
        conn.close()

        if rows:
            first_row = rows[0]  
            return jsonify({
                'time': first_row[0],
                'temp': first_row[1],
                'humidity': first_row[2]
            })
        else:
            return jsonify({
                'time': "none",
                'temp': "none",
                'humidity': "none"
            }),200
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Please use YYYY-MM-DDTHH:MM.'}), 400
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

