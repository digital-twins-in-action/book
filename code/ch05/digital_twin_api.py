from flask import Flask, request, jsonify
from flask_cors import CORS
import graphene
from graphene import ObjectType, String, List, Float
from neo4j import GraphDatabase, basic_auth, exceptions as neo4j_exceptions
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import os
from typing import Dict, Any

# Initialize DynamoDB client
try:
    dynamodb = boto3.client(
        "dynamodb",
        endpoint_url="http://localhost:8000",
        region_name="us-east-1",
    )
    print("Successfully connected to DynamoDB.")
except ClientError as e:
    print(f"Error connecting to DynamoDB: {e}")
    dynamodb = None

# Initialize Neo4j driver in order to be able to run in Lambda
# NOTE: Neo4j uses different environment variables for connection details
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")

try:
    # Use GraphDatabase.driver for Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth("", ""))
    # Verify connection
    driver.verify_connectivity()
    print("Successfully connected to Neo4j.")
except neo4j_exceptions.ServiceUnavailable as e:
    print(f"Error connecting to Neo4j: {e}")
    driver = None
except Exception as e:
    print(f"General error connecting to Neo4j: {e}")
    driver = None


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
    x = Float()
    y = Float()


class Document(ObjectType):
    id = String(required=True)
    space = String(required=True)
    url = String(required=True)


class Image(ObjectType):
    id = String(required=True)
    space = String(required=True)
    url = String(required=True)


class Space(ObjectType):
    name = String(required=True)
    sensors = List(Sensor, required=True)
    documents = List(Document, required=True)
    images = List(Image, required=True)
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
        if not driver or not dynamodb:
            print("Database connection not available.")
            return []
        # Neo4j: Use a session to run the query
        try:
            with driver.session() as session:
                # Find sensors, documents, and images in the given space using Neo4j
                # NOTE: Cypher query is compatible with Neo4j
                cypher_query = """
                    MATCH (startNode {name: $space_name})<-[:isPartOf|locatedIn*0..]-(node)
                    OPTIONAL MATCH (node)<-[:serves]-(sensor)
                    OPTIONAL MATCH (node)-[:hasDocument]->(document)
                    OPTIONAL MATCH (node)-[:hasImage]->(image)
                    RETURN 
                        node.name AS spaceName, 
                        sensor.sensorId AS sensorId,
                        sensor.x AS sensorX,
                        sensor.y AS sensorY,
                        document.url AS documentUrl, 
                        image.url as imageUrl
                """

                # Use session.run() and access records
                neo4j_results = session.run(cypher_query, space_name=space).data()

        except neo4j_exceptions.CypherError as e:
            print(f"Neo4j Cypher Error: {e}")
            return []
        except Exception as e:
            print(f"An unexpected Neo4j error occurred: {e}")
            return []

        if not neo4j_results:
            return []

        # Separate sensors, documents, and images from results
        memgraph_sensors = (
            []
        )  # Keeping the variable name for minimal change in subsequent logic
        memgraph_documents = []
        memgraph_images = []

        # Iterate over the dict results from session.run().data()
        for row in neo4j_results:
            space_name = row.get("spaceName")
            sensor_id = row.get("sensorId")
            sensor_x = row.get("sensorX")
            sensor_y = row.get("sensorY")
            document_url = row.get("documentUrl")
            image_url = row.get("imageUrl")

            # Check for spaceName since results might contain partial data
            if not space_name:
                continue

            if sensor_id and sensor_id != "":
                # NOTE: The coordinates need to be handled, ensuring they are floats if present
                memgraph_sensors.append(
                    {
                        "spaceName": space_name,
                        "sensorId": sensor_id,
                        "sensorX": float(sensor_x) if sensor_x is not None else None,
                        "sensorY": float(sensor_y) if sensor_y is not None else None,
                    }
                )

            if document_url and document_url != "":
                memgraph_documents.append(
                    {"spaceName": space_name, "documentUrl": document_url}
                )

            if image_url and image_url != "":
                memgraph_images.append({"spaceName": space_name, "imageUrl": image_url})

        # Convert ISO dates to Unix timestamps for DynamoDB
        start_ts = iso_to_timestamp(start_date)
        end_ts = iso_to_timestamp(end_date)

        # Get all sensor measurements from DynamoDB
        all_measurements = get_sensor_measurements_from_dynamo(
            memgraph_sensors, start_ts, end_ts
        )

        # Group data by space, sensors, documents, images and measurement type (Unchanged logic)
        spaces_data: Dict[str, Dict[str, Any]] = {}

        # Populate with sensors, documents, and images
        for s in memgraph_sensors:
            if s["spaceName"] not in spaces_data:
                spaces_data[s["spaceName"]] = {
                    "sensors": set(),
                    "documents": set(),
                    "images": set(),
                    "measurements": {},
                }
            spaces_data[s["spaceName"]]["sensors"].add(s["sensorId"])

        for d in memgraph_documents:
            if d["spaceName"] not in spaces_data:
                spaces_data[d["spaceName"]] = {
                    "sensors": set(),
                    "documents": set(),
                    "images": set(),
                    "measurements": {},
                }
            spaces_data[d["spaceName"]]["documents"].add(d["documentUrl"])

        for i in memgraph_images:
            if i["spaceName"] not in spaces_data:
                spaces_data[i["spaceName"]] = {
                    "sensors": set(),
                    "documents": set(),
                    "images": set(),
                    "measurements": {},
                }
            spaces_data[i["spaceName"]]["images"].add(i["imageUrl"])

        # Add measurements
        for record in all_measurements:
            space_name = record["spaceName"]
            sensor_id = record["sensor_id"]
            timestamp = record["timestamp"]

            if space_name not in spaces_data:
                spaces_data[space_name] = {
                    "sensors": set(),
                    "documents": set(),
                    "images": set(),
                    "measurements": {},
                }

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
        # Create a mapping for quick sensor lookup by ID for the Sensor object creation
        sensor_details_map = {s["sensorId"]: s for s in memgraph_sensors}

        for space_name, data in spaces_data.items():
            # Filter and create Sensor objects
            sensors = []
            for sensor_id in data["sensors"]:
                s = sensor_details_map.get(sensor_id)
                if s and s["spaceName"] == space_name:
                    sensors.append(
                        Sensor(
                            id=s["sensorId"],
                            space=s["spaceName"],
                            x=s["sensorX"],
                            y=s["sensorY"],
                        )
                    )

            documents = [
                Document(id=url, space=space_name, url=url) for url in data["documents"]
            ]
            images = [
                Image(id=url, space=space_name, url=url) for url in data["images"]
            ]

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
                Space(
                    name=space_name,
                    sensors=sensors,
                    documents=documents,
                    images=images,
                    measurements=measurement_groups,
                )
            )

        return results


def get_sensor_measurements_from_dynamo(sensors, start_timestamp, end_timestamp):
    all_measurements = []
    if not dynamodb:
        return all_measurements

    for sensor in sensors:
        try:
            # DynamoDB requires string values for ExpressionAttributeValues
            response = dynamodb.query(
                TableName="sensor-data",
                KeyConditionExpression="#pk = :sensor_id AND #sk BETWEEN :start AND :end",
                ExpressionAttributeNames={"#pk": "partKey", "#sk": "sortKey"},
                ExpressionAttributeValues={
                    ":sensor_id": {"S": sensor["sensorId"]},
                    # Timestamps are stored as Numbers in DynamoDB
                    ":start": {"N": str(start_timestamp)},
                    ":end": {"N": str(end_timestamp)},
                },
            )
            for item in response.get("Items", []):
                # Ensure sortKey is handled correctly, it's a string from DynamoDB
                timestamp_str = item["sortKey"]["N"]
                measurement = {
                    "spaceName": sensor["spaceName"],
                    "sensor_id": item["partKey"]["S"],
                    "timestamp": timestamp_str,
                }
                for key, value in item.items():
                    if key not in ["partKey", "sortKey"] and "N" in value:
                        # Convert DynamoDB Number string to Python float
                        measurement[key] = float(value["N"])
                all_measurements.append(measurement)
        except ClientError as e:
            print(
                f"Error querying sensor {sensor['sensorId']}: {e.response['Error']['Message']}"
            )
        except Exception as e:
            print(
                f"General error processing DynamoDB results for {sensor['sensorId']}: {e}"
            )

    return all_measurements


def iso_to_timestamp(iso_string):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    # Return as string since DynamoDB expects string in ExpressionAttributeValues
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


schema = graphene.Schema(query=Query)
app = Flask(__name__)
CORS(app)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    try:
        data = request.get_json()
        query = data.get("query")
        # Ensure variables are handled if present
        variables = data.get("variables")
        result = schema.execute(query, variables=variables)

        if result.errors:
            # Log errors for debugging
            print(f"GraphQL Errors: {result.errors}")
            # Return errors in the response
            return jsonify(
                {"data": result.data, "errors": [str(e) for e in result.errors]}
            )

        return jsonify(result.data)
    except Exception as e:
        print(f"GraphQL Request Error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/")
def index():
    return "GraphQL server is running. Send POST requests to /graphql."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
