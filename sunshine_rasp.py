import paho.mqtt.client as mqtt
import threading
import time
import board
import busio
from threading import Thread, Lock
import adafruit_bme280
import adafruit_ccs811

mutex = Lock()
broker_address="broker.hivemq.com"
port = 1883

## Measurement Frequency (seconds) default = 10s ##
measFreqTemp = 3
measFreqHum = 5
measFreqTvoc = 7
measFreqCo2 = 11

## COMMON FOR MQTT ##
def onMessage(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    topicVariableMapper(message.topic, str(message.payload.decode("utf-8")))
    printCurrentFreqs()

def onConnect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("rasp0FreqTemp") 
    client.subscribe("rasp0FreqHum") 
    client.subscribe("rasp0FreqTvoc") 
    client.subscribe("rasp0FreqCo2") 

def onLog(client, userdata, level, buf):
    print("log: ",buf)

## LOGIC ##
def printCurrentFreqs(): 
    global measFreqTemp
    global measFreqHum  
    global measFreqTvoc
    global measFreqCo2
    print("Current measFreqTemp", measFreqTemp)
    print("Current measFreqHum", measFreqHum)
    print("Current measFreqTvoc", measFreqTvoc)
    print("Current measFreqCo2", measFreqCo2)

def topicVariableMapper(topic, value):
    mutex.acquire()
    try:
        if topic == "rasp0FreqTemp":
            print(value)
            global measFreqTemp
            measFreqTemp = int(value)
        elif topic == "rasp0FreqHum":
            print(value)
            global measFreqHum
            measFreqHum = int(value)
        elif topic == "rasp0FreqTvoc":
            print(value)
            global measFreqTvoc
            measFreqTvoc = int(value)
        elif topic == "rasp0FreqCo2":
            global measFreqCo2
            measFreqCo2 = int(value)
            print(value)
        else:
            print("Invalid topic")
    finally:
        mutex.release()

def sendTemperature():
    while True:
        temp = bme280.temperature
        if temp > 0:
            client.publish("rasp0_temperature", temp)

        mutex.acquire()
        try:
            global measFreqTemp
            measFreqTempLocal = measFreqTemp
        finally:
            mutex.release()

        print("function ~~ SendTemperature()", measFreqTempLocal) # debug
        time.sleep(measFreqTempLocal)

def sendHumidity():
    while True:
        hum = bme280.relative_humidity 
        if hum > 0:
            client.publish("rasp0_humidity", hum)

        mutex.acquire()
        try:
            global measFreqHum
            measFreqHumLocal = measFreqHum
        finally:
            mutex.release()

        print("function ~~ sendHumidity()", measFreqHumLocal) # debug
        time.sleep(measFreqHumLocal)

def sendTvoc():
    while True:
        if ccs811.data_ready:
            tvoc = ccs811.tvoc
        #   if tvoc > 0:
            client.publish("rasp0_tvoc", tvoc)
        else:
            print("ERROR CCS811 don't ready for read measurement")
        
        mutex.acquire()
        try:
            global measFreqTvoc
            measFreqTvocLocal = measFreqTvoc
        finally:
            mutex.release()

        print("function ~~ sendTvoc()", measFreqTvocLocal) # debug
        time.sleep(measFreqTvocLocal)

def sendCo2():
    while True:
        if ccs811.data_ready:
            co2 = ccs811.eco2
        #   if tvoc > 0:
            client.publish("rasp0_co2", co2)
        else:
            print("ERROR CCS811 don't ready for read measurement")

        mutex.acquire()
        try:
            global measFreqCo2
            measFreqCo2Local = measFreqCo2
        finally:
            mutex.release()

        print("function ~~ sendCo2()", measFreqCo2Local) # debug
        time.sleep(measFreqCo2Local)

## SENSOR INIT ##
i2c = busio.I2C(board.SCL, board.SDA)
ccs811 = adafruit_ccs811.CCS811(i2c)

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.mode = adafruit_bme280.MODE_NORMAL
bme280.standby_period = adafruit_bme280.STANDBY_TC_500
bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
time.sleep(1)

## MQTT INIT ##
printCurrentFreqs()
print("creating new client Raspberry")
client = mqtt.Client("Raspberry0")
client.on_message=onMessage
client.on_log=onLog
client.on_connect=onConnect
print("connecting to broker")
client.connect(broker_address, port)
client.loop_start()

## THREADS INIT ##
tempSenderThread = threading.Thread(target=sendTemperature)
humSenderThread = threading.Thread(target=sendHumidity)
tvocSenderThread = threading.Thread(target=sendTvoc)
co2SenderThread = threading.Thread(target=sendCo2)

tempSenderThread.daemon = True
humSenderThread.daemon = True
tvocSenderThread.daemon = True
co2SenderThread.daemon = True

tempSenderThread.start()
humSenderThread.start()
tvocSenderThread.start()
co2SenderThread.start()

while True:
    pass
