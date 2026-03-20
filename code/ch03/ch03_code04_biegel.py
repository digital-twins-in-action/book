import base64, struct


def decode_sensor_message(base64_payload):
    raw_bytes = base64.b64decode(base64_payload)

    temp_raw = struct.unpack(">h", raw_bytes[0:2])[0]
    temperature = temp_raw / 100.0

    humidity_raw = struct.unpack(">H", raw_bytes[2:4])[0]
    humidity = humidity_raw / 10.0

    return {"temperature": temperature, "humidity": humidity, "unit": "celsius"}


payload = "B1QDOH//AWhRYAQ="
data = decode_sensor_message(payload)
print(f"Raw data: B1QDOH//AWhRYAQ=")
print(f"Temperature: {data['temperature']}°C")
print(f"Humidity: {data['humidity']}%")
