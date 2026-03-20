import json
import base64
import struct
import os
import boto3
from datetime import datetime, timezone
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sqs_client = boto3.client("sqs")
QUEUE_URL = os.environ["SQS_QUEUE_URL"]


def decode_lht52(payload_data: str) -> dict:
    """Decodes LHT52 temperature and humidity payload."""
    raw_bytes = base64.b64decode(payload_data)
    if len(raw_bytes) < 4:
        raise ValueError("LHT52 payload too short.")

    temp_raw, humidity_raw = struct.unpack(">hH", raw_bytes[0:4])

    return {
        "temperature": round(temp_raw / 100.0, 2),
        "humidity": round(humidity_raw / 10.0, 1),
    }


def decode_lwl02(payload_data: str) -> dict:
    """Decodes LWL02 water leak sensor payload."""
    payload_bytes = base64.b64decode(payload_data)
    if len(payload_bytes) < 10:
        raise ValueError("LWL02 payload too short.")

    status_bat, mode, total_events_raw, last_duration_raw, alarm = struct.unpack(
        ">H B 3s 3s B", payload_bytes
    )

    total_events = int.from_bytes(total_events_raw, "big")
    last_duration = int.from_bytes(last_duration_raw, "big")

    return {
        "battery_voltage_v": round((status_bat & 0x3FFF) / 1000.0, 3),
        "leak_detected": bool((status_bat >> 14) & 0x01),
        "total_leak_events": total_events,
        "last_leak_duration_minutes": last_duration,
        "alarm_active": bool(alarm & 0x01),
        "mode": mode,
    }


# Map sensor IDs to their decoding functions
SENSOR_DECODERS = {
    "temp_sensor_1": decode_lht52,
    "leak_sensor_1": decode_lwl02,
}


# --- Main Lambda Handler ---
def lambda_handler(event: dict, context: object) -> dict:
    """Processes and routes LoRaWAN sensor data."""
    try:
        # Validate and extract core data from event
        lorawan_meta = event.get("WirelessMetadata", {}).get("LoRaWAN", {})
        topic = event.get("topic")
        dev_eui = lorawan_meta.get("DevEui")
        payload = event.get("PayloadData")

        if not all([topic, dev_eui, payload]):
            raise ValueError("Missing required event data.")

        # Parse topic for metadata
        topic_parts = topic.split("/")
        if len(topic_parts) < 4:
            raise ValueError("Invalid topic format.")
        location, measurement_type, place, sensor_id = topic_parts[:4]

        logger.info(f"Processing sensor {sensor_id} from {place} ({dev_eui})")

        # Decode payload using the appropriate decoder
        decoder = SENSOR_DECODERS.get(sensor_id)
        if not decoder:
            raise ValueError(f"No decoder for sensor ID: '{sensor_id}'.")

        decoded_readings = decoder(payload)

        # Enrich the data and prepare for SQS
        enriched_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": location,
            "measurement_type": measurement_type,
            "place": place,
            "sensor_id": sensor_id,
            "dev_eui": dev_eui,
            "readings": decoded_readings,
            "request_id": context.aws_request_id,
        }

        # Route to SQS
        sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(enriched_data),
            MessageAttributes={
                "sensor_type": {"StringValue": measurement_type, "DataType": "String"},
                "location": {"StringValue": location, "DataType": "String"},
                "sensor_id": {"StringValue": sensor_id, "DataType": "String"},
                "dev_eui": {"StringValue": dev_eui, "DataType": "String"},
            },
        )

        logger.info(f"Successfully sent data to SQS for device {dev_eui}.")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data processed successfully."}),
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except ClientError as e:
        logger.error(f"AWS service error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "AWS service error."})}
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "An internal error occurred."}),
        }
