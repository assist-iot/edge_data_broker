import paho.mqtt.client as paho
import json, time

#broker= "10.0.2.15"
broker= "127.0.0.1"
port  = 31883
topic = "assist.test"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc, test):
    print("Connected with result code "+str(rc))

def on_publish(client,userdata,result):                    # create function for callback
    print("data published!")
    pass

client1= paho.Client("control1")                           # create client object
client1.on_publish = on_publish                            # assign function to callback
client1.on_connect = on_connect
client1.connect(broker,port)                               # establish connection
print("Connected to MQTT")
body = {}
body["name"] = "DeviceName"
body["raw-data"] = 1.000

i = 0
while i < 1000 :
    body["raw-data"] = float(i)
    bodyS = json.dumps(body)
    print("Publishig data: " + bodyS)
    ret= client1.publish(topic, bodyS)               # publish
    i += 1
    time.sleep(0.1)
