my_pos = (0.1, 3)

sensors = [
    {"id": "flow_meter_1", "name": "Rear garden tap", "pos": (0.839, 0.5)},
    {"id": "flow_meter_2", "name": "Front garden tap", "pos": (0.875, 18.31)},
    {"id": "water_main_meter", "name": "Main water meter", "pos": (3.13, 21.99)},
]

dist = lambda p1, p2: ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

print("Sensors within 5m:")
[
    print(f"- {s['name']}: {d:.1f}m")
    for s in sensors
    if (d := dist(my_pos, s["pos"])) <= 5
]
