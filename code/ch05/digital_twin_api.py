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

# --- Database Initialization ---
try:
    dynamodb = boto3.client(
        "dynamodb",
        region_name="us-east-1",
    )
    print("Successfully connected to DynamoDB.")
except ClientError as e:
    print(f"Error connecting to DynamoDB: {e}")
    dynamodb = None

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth("", ""))
    driver.verify_connectivity()
    print("Successfully connected to Memgraph/Neo4j.")
except Exception as e:
    print(f"Error connecting to Graph DB: {e}")
    driver = None

# --- GraphQL Types ---


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


class TreeNode(ObjectType):
    name = String()
    label = String()
    children = List(lambda: TreeNode)


# --- Query Resolvers ---


class Query(ObjectType):
    spaces = List(
        Space,
        space=String(required=True),
        start_date=String(required=True),
        end_date=String(required=True),
    )

    tree = graphene.Field(TreeNode, root_node=String(required=True))

    # 1. Update the Resolver to use the standard driver records instead of .data()
    def resolve_tree(self, info, root_node):
        if not driver:
            return None
        # We change the Cypher to return the path 'p' directly
        cypher_query = """
        MATCH p = (start {name: $root_name})<-[:isPartOf|locatedIn*0..]-(child)
        RETURN p
        """
        try:
            with driver.session() as session:
                # Remove .data() here to keep the native Node objects
                results = session.run(cypher_query, root_name=root_node)
                return build_tree_structure(results, root_node)
        except Exception as e:
            print(f"Hierarchy Error: {e}")
            return None

    def resolve_spaces(self, info, space, start_date, end_date):
        if not driver or not dynamodb:
            return []

        try:
            with driver.session() as session:
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
                neo4j_results = session.run(cypher_query, space_name=space).data()
        except Exception as e:
            print(f"Neo4j error: {e}")
            return []

        if not neo4j_results:
            return []

        memgraph_sensors = []
        memgraph_documents = []
        memgraph_images = []

        for row in neo4j_results:
            space_name = row.get("spaceName")
            if not space_name:
                continue

            if row.get("sensorId"):
                memgraph_sensors.append(
                    {
                        "spaceName": space_name,
                        "sensorId": row["sensorId"],
                        "sensorX": (
                            float(row["sensorX"])
                            if row["sensorX"] is not None
                            else None
                        ),
                        "sensorY": (
                            float(row["sensorY"])
                            if row["sensorY"] is not None
                            else None
                        ),
                    }
                )
            if row.get("documentUrl"):
                memgraph_documents.append(
                    {"spaceName": space_name, "documentUrl": row["documentUrl"]}
                )
            if row.get("imageUrl"):
                memgraph_images.append(
                    {"spaceName": space_name, "imageUrl": row["imageUrl"]}
                )

        start_ts = iso_to_timestamp(start_date)
        end_ts = iso_to_timestamp(end_date)
        all_measurements = get_sensor_measurements_from_dynamo(
            memgraph_sensors, start_ts, end_ts
        )

        # Re-incorporating your grouping logic
        spaces_data = {}
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

        for record in all_measurements:
            sn = record["spaceName"]
            sid = record["sensor_id"]
            ts = record["timestamp"]
            if sn not in spaces_data:
                spaces_data[sn] = {
                    "sensors": set(),
                    "documents": set(),
                    "images": set(),
                    "measurements": {},
                }
            spaces_data[sn]["sensors"].add(sid)
            for key, value in record.items():
                if key not in ["spaceName", "sensor_id", "timestamp"]:
                    if key not in spaces_data[sn]["measurements"]:
                        spaces_data[sn]["measurements"][key] = []
                    spaces_data[sn]["measurements"][key].append(
                        {"sensor_id": sid, "timestamp": ts, "value": float(value)}
                    )

        results = []
        sensor_details_map = {s["sensorId"]: s for s in memgraph_sensors}

        for space_name, data in spaces_data.items():
            sensors = [
                Sensor(
                    id=sid,
                    space=space_name,
                    x=sensor_details_map.get(sid, {}).get("sensorX"),
                    y=sensor_details_map.get(sid, {}).get("sensorY"),
                )
                for sid in data["sensors"]
            ]
            documents = [
                Document(id=url, space=space_name, url=url) for url in data["documents"]
            ]
            images = [
                Image(id=url, space=space_name, url=url) for url in data["images"]
            ]

            m_groups = []
            for m_type, vals in data["measurements"].items():
                ms = [
                    Measurement(
                        sensor_id=v["sensor_id"],
                        timestamp=v["timestamp"],
                        value=v["value"],
                    )
                    for v in vals
                ]
                m_groups.append(
                    MeasurementGroup(
                        name=m_type,
                        unit=get_unit_for_measurement_type(m_type),
                        values=ms,
                    )
                )

            results.append(
                Space(
                    name=space_name,
                    sensors=sensors,
                    documents=documents,
                    images=images,
                    measurements=m_groups,
                )
            )

        return results


# --- Helper Functions ---


# 2. Update the Helper to handle native Node objects
def build_tree_structure(results, root_name):
    nodes_map = {}

    for record in results:
        # 'p' is a Path object
        path = record["p"]
        path_nodes = path.nodes  # These are native Node objects

        for i, node in enumerate(path_nodes):
            # Accessing properties from a native Node object
            name = node.get("name")

            # Native Node objects have a 'labels' set
            label = list(node.labels)[0] if node.labels else "Entity"

            if name not in nodes_map:
                nodes_map[name] = {"name": name, "label": label, "children_map": {}}

            if i > 0:
                parent_name = path_nodes[i - 1].get("name")
                if name not in nodes_map[parent_name]["children_map"]:
                    nodes_map[parent_name]["children_map"][name] = nodes_map[name]

    def format_node(node_dict):
        # Sort children by name to keep the tree consistent
        sorted_children = sorted(
            node_dict["children_map"].values(), key=lambda x: x["name"]
        )
        return TreeNode(
            name=node_dict["name"],
            label=node_dict["label"],
            children=[format_node(c) for c in sorted_children],
        )

    return format_node(nodes_map[root_name]) if root_name in nodes_map else None


def get_sensor_measurements_from_dynamo(sensors, start_timestamp, end_timestamp):
    all_measurements = []
    if not dynamodb:
        return all_measurements
    for sensor in sensors:
        try:
            response = dynamodb.query(
                TableName="sensor-data",
                KeyConditionExpression="#pk = :sensor_id AND #sk BETWEEN :start AND :end",
                ExpressionAttributeNames={"#pk": "partKey", "#sk": "sortKey"},
                ExpressionAttributeValues={
                    ":sensor_id": {"S": sensor["sensorId"]},
                    ":start": {"N": str(start_timestamp)},
                    ":end": {"N": str(end_timestamp)},
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
        except Exception as e:
            print(f"Dynamo Error: {e}")
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


# --- Flask App ---
schema = graphene.Schema(query=Query)
app = Flask(__name__)
CORS(app)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    try:
        data = request.get_json()
        result = schema.execute(data.get("query"), variables=data.get("variables"))
        if result.errors:
            return jsonify(
                {"data": result.data, "errors": [str(e) for e in result.errors]}
            )
        return jsonify({"data": result.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
