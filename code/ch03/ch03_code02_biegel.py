import paho.mqtt.client as mqtt
import json, time

BROKER = "test.mosquitto.org"  # Free public broker
TOPIC = "test/sensor/temperature"

# Callback when message received
def on_message(client, userdata, message):
    print(f"Message Received: {message.payload} on topic {message.topic}")

# Create client and connect
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER)

# Subscribe to topic
client.subscribe("#")
client.loop_start()  # Start listening in background

# Publish messages
for i in range(5):
    temp = 20 + i
    client.publish(TOPIC, json.dumps({"temperature": temp}))
    print(f"Message Sent: {temp}°C")
    time.sleep(2)

# Cleanup
client.loop_stop()
client.disconnect()