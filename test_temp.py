import board
import adafruit_dht
 
dht_device = adafruit_dht.DHT22(board.D25)
 
try:
    temperature = dht_device.temperature
    humidity = dht_device.humidity
    print("temperature: {:.1f}C humidity: {}%".format(temperature, humidity))
except RuntimeError as e:
    print("something wrong:", e)
 
dht_device.exit()
