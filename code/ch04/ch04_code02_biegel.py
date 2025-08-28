# UTM Zone 50S coordinates (meters) for Perth area
my_pos = (384850, 6463020)  # Your position in UTM

sensors = [
    {"id": "temp_sensor_1", "name": "Living Room", "pos": (384845, 6463010)},
    {"id": "temp_sensor_2", "name": "Garden", "pos": (384855, 6463025)},
    {"id": "flow_meter_1", "name": "Front Tap", "pos": (384848, 6463018)},
    {"id": "power_meter_1", "name": "Meter Box", "pos": (384852, 6463015)},
]

# Simple Euclidean distance for UTM (already in meters)
dist = lambda p1, p2: ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5

print("Sensors within 5m:")
[print(f"- {s['name']}: {d:.1f}m") for s in sensors if (d := dist(my_pos, s['pos'])) <= 5]