import simpy
import random

MAX_POWER = 7.0
APPLIANCES = [
    ("Washer", 2.0, 45, 5),  # 45 min avg, varies by ~5 min
    ("Dryer", 3.0, 40, 5),
    ("Dishwasher", 1.5, 60, 2),
    ("EV", 5.0, 120, 10),
]


def appliance(env, name, power, avg_duration, std_dev, power_grid):
    start_delay = random.uniform(0, 10)
    yield env.timeout(start_delay)

    print(f"[{env.now:5.1f}m] {name} requests {power}kW")

    yield power_grid.get(power)

    actual_duration = random.gauss(avg_duration, std_dev)
    actual_duration = max(1, actual_duration)

    print(f"[{env.now:5.1f}m] {name} START for {actual_duration:.1f}m")

    yield env.timeout(actual_duration)
    yield power_grid.put(power)

    print(f"[{env.now:5.1f}m] {name} END")


env = simpy.Environment()
grid = simpy.Container(env, capacity=MAX_POWER, init=MAX_POWER)

for name, power, avg_dur, std_dev in APPLIANCES:
    env.process(appliance(env, name, power, avg_dur, std_dev, grid))

env.run()
