from flask import Flask, request, jsonify
import graphene
from graphene import ObjectType, String, List, Float
import json
import mgclient
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import os

# --- 1. Client Initialization ---
try:
    dynamodb = boto3.client(
        "dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1")
    )
    print("Successfully connected to DynamoDB.")
except ClientError as e:
    print(f"Error connecting to DynamoDB: {e}")
    dynamodb = None

try:
    conn = mgclient.connect(
        host=os.environ.get("MEMGRAPH_HOST", "127.0.0.1"),
        port=int(os.environ.get("MEMGRAPH_PORT", 7687)),
    )
    print("Successfully connected to Memgraph.")
except Exception as e:
    print(f"Error connecting to Memgraph: {e}")
    conn = None


# --- 2. GraphQL Schema Definitions ---
class Measurement(ObjectType):
    sensor_id = String(required=True)
    timestamp = String(required=True)
    value = Float(required=True)


class MeasurementGroup(ObjectType):
    name = String(required=True)
    unit = String()
    values = List(Measurement, required=True)


class Sensor(ObjectType):
    id = String(required=True)
    space = String(required=True)


class Space(ObjectType):
    name = String(required=True)
    sensors = List(Sensor, required=True)
    measurements = List(MeasurementGroup, required=True)


class Query(ObjectType):
    spaces = List(
        Space,
        space=String(required=True, description="The name of the space to query."),
        start_date=String(
            required=True,
            description="The start date for the data query (ISO 8601 format).",
        ),
        end_date=String(
            required=True,
            description="The end date for the data query (ISO 8601 format).",
        ),
    )

    def resolve_spaces(self, info, space, start_date, end_date):
        if not conn or not dynamodb:
            return []

        # Find sensors in the given space using Memgraph
        cypher_query = """
            MATCH (startNode {name: $space_name})<-[:isPartOf|locatedIn*0..]-(node)<-[:serves]-(sensor)
            RETURN node.name AS spaceName, sensor.sensorId AS sensorId
        """
        cursor = conn.cursor()
        cursor.execute(cypher_query, {"space_name": space})
        memgraph_sensors = [
            {"spaceName": row[0], "sensorId": row[1]}
            for row in cursor.fetchall()
            if row[1] is not None and row[1] != ""
        ]

        print(memgraph_sensors)
        if not memgraph_sensors:
            return []

        # Convert ISO dates to Unix timestamps for DynamoDB
        start_ts = iso_to_timestamp(start_date)
        end_ts = iso_to_timestamp(end_date)

        # Get all sensor measurements from DynamoDB
        all_measurements = get_sensor_measurements_from_dynamo(
            memgraph_sensors, start_ts, end_ts
        )

        # Group data by space and measurement type
        spaces_data = {}
        for record in all_measurements:
            space_name = record["spaceName"]
            sensor_id = record["sensor_id"]
            timestamp = record["timestamp"]

            if space_name not in spaces_data:
                spaces_data[space_name] = {"sensors": set(), "measurements": {}}

            spaces_data[space_name]["sensors"].add(sensor_id)

            for key, value in record.items():
                if key not in ["spaceName", "sensor_id", "timestamp"]:
                    if key not in spaces_data[space_name]["measurements"]:
                        spaces_data[space_name]["measurements"][key] = []
                    spaces_data[space_name]["measurements"][key].append(
                        {
                            "sensor_id": sensor_id,
                            "timestamp": timestamp,
                            "value": float(value),
                        }
                    )

        # Build the final GraphQL response
        results = []
        for space_name, data in spaces_data.items():
            sensors = [Sensor(id=sid, space=space_name) for sid in data["sensors"]]

            measurement_groups = []
            for measurement_type, values in data["measurements"].items():
                measurements = [
                    Measurement(
                        sensor_id=val["sensor_id"],
                        timestamp=val["timestamp"],
                        value=val["value"],
                    )
                    for val in values
                ]
                unit = get_unit_for_measurement_type(measurement_type)
                measurement_groups.append(
                    MeasurementGroup(
                        name=measurement_type, unit=unit, values=measurements
                    )
                )

            results.append(
                Space(name=space_name, sensors=sensors, measurements=measurement_groups)
            )

        return results


# --- 3. Helper Functions ---
def get_sensor_measurements_from_dynamo(sensors, start_timestamp, end_timestamp):
    all_measurements = []
    for sensor in sensors:
        try:
            response = dynamodb.query(
                TableName="sensor-data",
                KeyConditionExpression="partKey = :sensor_id AND sortKey BETWEEN :start AND :end",
                ExpressionAttributeValues={
                    ":sensor_id": {"S": sensor["sensorId"]},
                    ":start": {"N": start_timestamp},
                    ":end": {"N": end_timestamp},
                },
            )
            for item in response.get("Items", []):
                measurement = {
                    "spaceName": sensor["spaceName"],
                    "sensor_id": item["partKey"]["S"],
                    "timestamp": item["sortKey"]["N"],
                }
                for key, value in item.items():
                    if key not in ["partKey", "sortKey"] and "N" in value:
                        measurement[key] = float(value["N"])
                all_measurements.append(measurement)
        except ClientError as e:
            print(
                f"Error querying sensor {sensor['sensorId']}: {e.response['Error']['Message']}"
            )
    return all_measurements


def iso_to_timestamp(iso_string):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return str(int(dt.timestamp() * 1000))


def get_unit_for_measurement_type(measurement_type):
    unit_mapping = {
        "temperature": "°C",
        "humidity": "%",
        "pressure": "hPa",
        "co2": "ppm",
        "power": "W",
        "current": "A",
    }
    return unit_mapping.get(measurement_type.lower(), "units")


# --- 4. Flask Application Setup ---
schema = graphene.Schema(query=Query)
app = Flask(__name__)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    try:
        data = request.get_json()
        query = data.get("query")
        result = schema.execute(query)
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/")
def index():
    return "GraphQL server is running. Send POST requests to /graphql."


if __name__ == "__main__":
    app.run(debug=True)
