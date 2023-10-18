import random
import time
import sys
from paho.mqtt import client as mqtt_client

broker = "localhost"
port = 31883
topic = "geo/2"
#topic = "worker/heartbeat"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def auto_publish(value):
    while True:
        result = client.publish(topic,value)
        status = result[0]
        if status == 0:
            print(f"Send `{value}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

def publish(client):
    while True:
        time.sleep(1)
        value = input('Enter the message:')
        result = client.publish(topic,value)
        status = result[0]
        if status == 0:
            print(f"Send `{value}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

def run():
    try:
        global client
        client = connect_mqtt()
        client.loop_start()
        publish(client)
    except Exception:
        client.disconnect()
        client.loop_stop()
    sys.exit(0)

if __name__ == '__main__':
    run()