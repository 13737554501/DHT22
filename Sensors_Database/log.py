import time
import sqlite3
import adafruit_dht
import board
dbname='/home/yelone/DHT22/Sensors_Database/sensorsData.db'
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
	
	conn1=sqlite3.connect(dbname)
	curs=conn1.cursor()
	
	curs.execute("INSERT INTO DHT_data values(datetime('now', '+8 hours'), (?), (?))", (temp, hum))
	conn1.commit()
	conn1.close()

# main function
def main():
	temp, hum = getDHTdata()
	logData (temp, hum)
	print(temp)
# ------------ Execute program 
main()

