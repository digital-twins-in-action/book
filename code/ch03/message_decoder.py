import json, base64, struct
from datetime import datetime


def decode_lht52_sensor(payload):
    raw_bytes = base64.b64decode(payload["data"])
    temp_raw = struct.unpack(">h", raw_bytes[0:2])
    humidity_raw = struct.unpack(">H", raw_bytes[2:4])

    return {
        "temperature": temp_raw / 100.0,
        "humidity": humidity_raw / 10.0,
    }


def decode_lwl02_sensor(payload):
    payload_bytes = base64.b64decode(payload)

    status_bat, mod = struct.unpack(">HB", payload_bytes[0:3])
    total_events = int.from_bytes(payload_bytes[3:6], "big")
    last_duration = int.from_bytes(payload_bytes[6:9], "big")
    alarm = payload_bytes[9]
    battery_mv = status_bat & 0x3FFF
    leak_detected = (status_bat >> 14) & 0x01
    alarm_active = alarm & 0x01

    return {
        "battery_voltage_v": round(battery_mv / 1000.0, 3),
        "leak_detected": bool(leak_detected),
        "total_leak_events": total_events,
        "last_leak_duration_minutes": last_duration,
        "alarm_active": bool(alarm_active),
    }


def route_to_storage(enriched_data):
    # For now, no actual routing to storage is performed just yet
    print(enriched_data)


SENSOR_DECODERS = {
    "temp_sensor_1": decode_lht52_sensor,
    "leak_sensor_1": decode_lwl02_sensor,
}


def lambda_handler(event, context):
    topic = event["topic"]
    payload = event["PayloadData"]
    dev_eui = event["WirelessMetadata"]["LoRaWAN"]["DevEui"]

    topic_parts = topic.split("/")
    location = topic_parts[0]
    measurement_type = topic_parts[1]
    place = topic_parts[2]
    sensor_id = topic_parts[3]

    decoder = SENSOR_DECODERS.get(sensor_id)
    decoded_data = decoder(payload)

    enriched_data = {
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "measurement_type": measurement_type,
        "place": place,
        "sensor_id": sensor_id,
        "readings": decoded_data,
        "dev_eui": dev_eui,
    }

    route_to_storage(enriched_data)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Processed successfully",
            }
        ),
    }
