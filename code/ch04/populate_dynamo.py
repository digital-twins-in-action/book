import boto3
from botocore.exceptions import ClientError
import time


def setup_dynamodb():
    # Create DynamoDB client for local instance
    dynamodb = boto3.client(
        "dynamodb",
        endpoint_url="http://localhost:8000",
        region_name="us-east-1",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )

    # Step 1: Create the sensor data table
    try:
        table_response = dynamodb.create_table(
            TableName="dtia_sensor_data",
            KeySchema=[
                {"AttributeName": "sensor_id", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "sensor_id", "AttributeType": "S"},  # String
                {"AttributeName": "timestamp", "AttributeType": "N"},  # Number
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print("Table 'dtia_sensor_data' created successfully")

        # Wait for table to be active (usually instant in local DynamoDB)
        time.sleep(1)

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("Table already exists, skipping creation")
        else:
            print(f"Error creating table: {e}")
            return

    # Step 2: Add sample sensor data (10 records across 2 sensors)
    sensor_readings = [
        # Sensor 1 readings
        {
            "sensor_id": {"S": "sensor_id1"},
            "timestamp": {"N": "1749945584458"},
            "humidity": {"N": "66.3"},
            "temperature": {"N": "16.4"},
        },
        {
            "sensor_id": {"S": "sensor_id1"},
            "timestamp": {"N": "1749946183884"},
            "humidity": {"N": "66.5"},
            "temperature": {"N": "16.4"},
        },
        {
            "sensor_id": {"S": "sensor_id1"},
            "timestamp": {"N": "1749946784664"},
            "humidity": {"N": "66.5"},
            "temperature": {"N": "16.5"},
        },
        {
            "sensor_id": {"S": "sensor_id1"},
            "timestamp": {"N": "1749947383975"},
            "humidity": {"N": "66.5"},
            "temperature": {"N": "16.5"},
        },
        {
            "sensor_id": {"S": "sensor_id1"},
            "timestamp": {"N": "1749947984123"},
            "humidity": {"N": "66.7"},
            "temperature": {"N": "16.6"},
        },
        # Sensor 2 readings
        {
            "sensor_id": {"S": "sensor_id2"},
            "timestamp": {"N": "1749945601234"},
            "humidity": {"N": "71.2"},
            "temperature": {"N": "18.3"},
        },
        {
            "sensor_id": {"S": "sensor_id2"},
            "timestamp": {"N": "1749946201456"},
            "humidity": {"N": "71.0"},
            "temperature": {"N": "18.5"},
        },
        {
            "sensor_id": {"S": "sensor_id2"},
            "timestamp": {"N": "1749946801789"},
            "humidity": {"N": "70.8"},
            "temperature": {"N": "18.7"},
        },
        {
            "sensor_id": {"S": "sensor_id2"},
            "timestamp": {"N": "1749947401012"},
            "humidity": {"N": "70.5"},
            "temperature": {"N": "18.9"},
        },
        {
            "sensor_id": {"S": "sensor_id2"},
            "timestamp": {"N": "1749948001345"},
            "humidity": {"N": "70.3"},
            "temperature": {"N": "19.1"},
        },
    ]

    # Insert each sensor reading
    for reading in sensor_readings:
        try:
            dynamodb.put_item(TableName="dtia_sensor_data", Item=reading)
            sensor = reading["sensor_id"]["S"]
            timestamp = reading["timestamp"]["N"]
            print(f"Added reading: {sensor} at {timestamp}")
        except ClientError as e:
            print(f"Error adding reading: {e}")

    print("\nSetup complete! Your sensor data table is ready for queries.")

    # Verify data was inserted
    try:
        response = dynamodb.scan(TableName="dtia_sensor_data")
        print(f"\nTable now contains {response['Count']} sensor readings")

        # Show summary by sensor
        sensor1_count = len(
            [
                item
                for item in response["Items"]
                if item["sensor_id"]["S"] == "sensor_id1"
            ]
        )
        sensor2_count = len(
            [
                item
                for item in response["Items"]
                if item["sensor_id"]["S"] == "sensor_id2"
            ]
        )
        print(f"sensor_id1: {sensor1_count} readings")
        print(f"sensor_id2: {sensor2_count} readings")

    except ClientError as e:
        print(f"Error verifying data: {e}")


if __name__ == "__main__":
    setup_dynamodb()
