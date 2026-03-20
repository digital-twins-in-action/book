import boto3

# Connect to local DynamoDB
db = boto3.client(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="us-east-1"
)

# Query sensor data in time range
response = db.query(
    TableName="sensor-data",
    KeyConditionExpression="partKey = :sensor AND sortKey BETWEEN :start AND :end",
    ExpressionAttributeValues={
        ":sensor": {"S": "a84041ce41845d13"},
        ":start": {"N": "1749719911402"},
        ":end": {"N": "1749919959402"},
    },
)

print(f"Found {response['Count']} readings:")
for item in response["Items"]:
    ts = item["sortKey"]["N"]
    temp = item["temperature"]["N"]
    humidity = item["humidity"]["N"]
    print(f"  {ts}: {temp}°C, {humidity}%")
