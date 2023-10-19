import paho.mqtt.client as mqtt

def run():
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("#")

    def on_message(client, userdata, msg):
        print(msg.topic+"-->"+str(msg.payload))

    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 31883, 60)
    client.loop_forever()

if __name__ == "__main__":
    run()