import time
import sqlite3
import adafruit_dht

import board
dbname='sensorsData.db'
sampleFreq = 1*60 # time in seconds ==> Sample each 1 min

# get data from DHT sensor
def getDHTdata():	
	dht_device = adafruit_dht.DHT22(board.D4)
	temp = dht_device.temperature
	hum = dht_device.humidity
	if hum is not None and temp is not None:
		hum = round(hum)
		temp = round(temp, 1)
	return temp, hum

#####

#
# log sensor data on database
def logData (temp, hum):
	try:
		conn=sqlite3.connect(dbname,check_same_thread=False)
		curs=conn.cursor()
		curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))", (temp, hum))
		conn.commit()
		print("Connected to the database successfully.")
	except sqlite3.Error as e:
		print(f"An error occurred while connecting to the database: {e}")
	finally:
		if conn:
			conn.close()

# main function
def main():
	while True:
		temp, hum = getDHTdata()
		logData (temp, hum)
		time.sleep(sampleFreq)

# ------------ Execute program 
main()

