from flask import Flask, request, jsonify
from flask_cors import CORS
import graphene
from graphene import ObjectType, String, List, Float
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from collections import defaultdict

try:
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    print("Successfully connected to DynamoDB.")
except ClientError as e:
    print(f"Error connecting to DynamoDB: {e}")
    dynamodb = None

# --- In-Memory Graph Data ---
IN_MEMORY_GRAPH = {
    "Pump Station": {
        "label": "Land",
        "children": [],
        "sensors": [
            {
                "name": "Pump",
                "sensorId": "a840418e165f3c76",
                "x": 50,
                "y": -50,
            }
        ],
    },
}


class Measurement(ObjectType):
    sensor_id, timestamp, value = (
        String(required=True),
        String(required=True),
        Float(required=True),
    )


class MeasurementGroup(ObjectType):
    name, unit, values = (
        String(required=True),
        String(),
        List(Measurement, required=True),
    )


class Sensor(ObjectType):
    id, name, space, x, y = (
        String(required=True),
        String(required=True),
        String(required=True),
        Float(),
        Float(),
    )


class Document(ObjectType):
    id, space, url = String(required=True), String(required=True), String(required=True)


class Image(ObjectType):
    id, space, url = String(required=True), String(required=True), String(required=True)


class Space(ObjectType):
    name, sensors, documents, images, measurements = (
        String(required=True),
        List(Sensor, required=True),
        List(Document, required=True),
        List(Image, required=True),
        List(MeasurementGroup, required=True),
    )


class TreeNode(ObjectType):
    name, label, children = String(), String(), List(lambda: TreeNode)


# --- Query Resolvers ---
class Query(ObjectType):
    spaces = List(
        Space,
        space=String(required=True),
        start_date=String(required=True),
        end_date=String(required=True),
    )
    tree = graphene.Field(TreeNode, root_node=String(required=True))

    def resolve_tree(self, info, root_node):
        return build_in_memory_tree(root_node)

    def resolve_spaces(self, info, space, start_date, end_date):
        if not dynamodb or not (descendants := get_all_descendants(space)):
            return []

        sensors, docs, imgs = [], [], []
        for node in descendants:
            data = IN_MEMORY_GRAPH.get(node, {})
            sensors.extend(
                [
                    {
                        "spaceName": node,
                        "sensorId": s.get("sensorId"),
                        "name": s.get("name"),
                        "sensorX": s.get("x"),
                        "sensorY": s.get("y"),
                    }
                    for s in data.get("sensors", [])
                ]
            )
            docs.extend(
                [
                    {"spaceName": node, "documentUrl": d["url"]}
                    for d in data.get("documents", [])
                ]
            )
            imgs.extend(
                [
                    {"spaceName": node, "imageUrl": i["url"]}
                    for i in data.get("images", [])
                ]
            )

        measurements = get_sensor_measurements_from_dynamo(
            sensors, iso_to_ts(start_date), iso_to_ts(end_date)
        )

        # Using defaultdict for automatic and concise nested grouping
        spaces_data = defaultdict(
            lambda: {
                "sensors": set(),
                "documents": set(),
                "images": set(),
                "measurements": defaultdict(list),
            }
        )

        for s in sensors:
            spaces_data[s["spaceName"]]["sensors"].add(s["sensorId"])
        for d in docs:
            spaces_data[d["spaceName"]]["documents"].add(d["documentUrl"])
        for i in imgs:
            spaces_data[i["spaceName"]]["images"].add(i["imageUrl"])

        for m in measurements:
            sn, sid, ts = m.pop("spaceName"), m.pop("sensor_id"), m.pop("timestamp")
            spaces_data[sn]["sensors"].add(sid)
            for k, v in m.items():
                spaces_data[sn]["measurements"][k].append(
                    {"sensor_id": sid, "timestamp": ts, "value": float(v)}
                )

        sensor_map = {s["sensorId"]: s for s in sensors}
        return [
            Space(
                name=name,
                sensors=[
                    Sensor(
                        id=sid,
                        space=name,
                        name=sensor_map.get(sid, {}).get("name"),
                        x=sensor_map.get(sid, {}).get("sensorX"),
                        y=sensor_map.get(sid, {}).get("sensorY"),
                    )
                    for sid in data["sensors"]
                ],
                documents=[
                    Document(id=url, space=name, url=url) for url in data["documents"]
                ],
                images=[Image(id=url, space=name, url=url) for url in data["images"]],
                measurements=[
                    MeasurementGroup(
                        name=m_type,
                        unit=get_unit(m_type),
                        values=[Measurement(**val) for val in vals],
                    )
                    for m_type, vals in data["measurements"].items()
                ],
            )
            for name, data in spaces_data.items()
        ]


# --- Helper Functions ---
def build_in_memory_tree(node_name):
    if node_name not in IN_MEMORY_GRAPH:
        return None
    node_data = IN_MEMORY_GRAPH[node_name]
    children = sorted(
        [
            c
            for name in node_data.get("children", [])
            if (c := build_in_memory_tree(name))
        ],
        key=lambda x: x.name,
    )
    return TreeNode(
        name=node_name, label=node_data.get("label", "Entity"), children=children
    )


def get_all_descendants(start_node, visited=None):
    visited = visited or set()
    if start_node not in IN_MEMORY_GRAPH or start_node in visited:
        return visited
    visited.add(start_node)
    for child in IN_MEMORY_GRAPH[start_node].get("children", []):
        get_all_descendants(child, visited)
    return visited


def get_sensor_measurements_from_dynamo(sensors, start_ts, end_ts):
    print(sensors)
    print(start_ts, end_ts)
    all_measurements = []
    for sensor in sensors:
        try:
            res = dynamodb.query(
                TableName="sensor-data",
                KeyConditionExpression="#pk = :sid AND #sk BETWEEN :start AND :end",
                ExpressionAttributeNames={"#pk": "partKey", "#sk": "sortKey"},
                ExpressionAttributeValues={
                    ":sid": {"S": sensor["sensorId"]},
                    ":start": {"N": start_ts},
                    ":end": {"N": end_ts},
                },
            )
            for item in res.get("Items", []):
                print(item)
                m = {
                    "spaceName": sensor["spaceName"],
                    "sensor_id": item["partKey"]["S"],
                    "timestamp": item["sortKey"]["N"],
                }
                m.update(
                    {
                        k: float(v["N"])
                        for k, v in item.items()
                        if k not in ["partKey", "sortKey"] and "N" in v
                    }
                )
                all_measurements.append(m)
        except Exception as e:
            print(f"Dynamo Error: {e}")
    print(all_measurements)
    return all_measurements


def iso_to_ts(iso_str):
    return str(
        int(datetime.fromisoformat(iso_str.replace("Z", "+00:00")).timestamp() * 1000)
    )


def get_unit(m_type):
    return {
        "temperature": "°C",
        "humidity": "%",
        "pressure": "hPa",
        "co2": "ppm",
        "power": "W",
        "current": "A",
    }.get(m_type.lower(), "units")


# --- Flask App ---
app = Flask(__name__)
CORS(app)
schema = graphene.Schema(query=Query)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    result = schema.execute(data.get("query"), variables=data.get("variables"))
    return jsonify(
        {"data": result.data, "errors": [str(e) for e in result.errors]}
        if result.errors
        else {"data": result.data}
    ), (400 if result.errors else 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
