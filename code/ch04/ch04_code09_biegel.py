import boto3

# Connect to local DynamoDB
db = boto3.client(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-east-1",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy",
)

# Query sensor data in time range
response = db.query(
    TableName="dtia_sensor_data",
    KeyConditionExpression="sensor_id = :sensor AND #ts BETWEEN :start AND :end",
    ExpressionAttributeNames={"#ts": "timestamp"},
    ExpressionAttributeValues={
        ":sensor": {"S": "sensor_id1"},
        ":start": {"N": "1749946000000"},
        ":end": {"N": "1749947500000"},
    },
)

print(f"Found {response['Count']} readings:")
for item in response["Items"]:
    ts = item["timestamp"]["N"]
    temp = item["temperature"]["N"]
    humidity = item["humidity"]["N"]
    print(f"  {ts}: {temp}°C, {humidity}%")
