import json
import os
from datetime import datetime, timezone
from decimal import Decimal
import logging
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])


def process_message_body(body: str) -> dict:
    """Parses and validates the JSON message body."""
    try:
        message = json.loads(body)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    required_fields = ["dev_eui", "timestamp", "readings"]
    if not all(field in message for field in required_fields):
        raise ValueError(f"Missing required field(s): {', '.join(required_fields)}")
    if not isinstance(message.get("readings"), dict):
        raise ValueError("'readings' must be a dictionary")

    return message


def convert_for_dynamodb(data: dict) -> dict:
    """Converts a dictionary's floats and timestamp for DynamoDB storage,
    breaking down readings into individual attributes."""
    # Convert timestamp to epoch
    try:
        dt_obj = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
        epoch_time = int(dt_obj.timestamp())
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {e}")

    # Build the final DynamoDB item with core attributes
    item = {
        "partKey": data["dev_eui"],
        "sortKey": epoch_time,
        "timestamp_iso": data["timestamp"],
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "ttl": epoch_time + (30 * 24 * 60 * 60),
    }

    # Break down readings and add them as individual attributes
    for key, value in data["readings"].items():
        if isinstance(value, float):
            item[key] = Decimal(str(value))
        else:
            item[key] = value

    return item


def save_item_to_dynamodb(item: dict, message_id: str):
    """Saves a single item to DynamoDB, handling duplicates."""
    try:
        # Add the message_id for conditional write to prevent duplicates
        item["message_id"] = message_id
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(message_id)",
        )
        logger.info(
            f"Successfully saved message {message_id} for device {item['partKey']}"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.warning(f"Duplicate message {message_id} detected. Skipping.")
        else:
            raise


def lambda_handler(event, context):
    """AWS Lambda handler to process a batch of SQS messages."""
    failures = []

    for record in event.get("Records", []):
        message_id = record.get("messageId")
        try:
            message_body = process_message_body(record.get("body"))
            dynamodb_item = convert_for_dynamodb(message_body)
            save_item_to_dynamodb(dynamodb_item, message_id)
        except Exception:
            logger.error(f"Failed to process message {message_id}.", exc_info=True)
            failures.append({"itemIdentifier": message_id})

    success_count = len(event.get("Records", [])) - len(failures)

    # Log summary
    logger.info(
        f"Batch processing complete. Success: {success_count}, Failed: {len(failures)}"
    )
    if failures:
        logger.warning(f"Failed message IDs: {[f['itemIdentifier'] for f in failures]}")

    return {"batchItemFailures": failures}
