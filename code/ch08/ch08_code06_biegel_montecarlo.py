import simpy
import random

# Fixed constants
MAX_POWER = 7.0
# Format: (Name, Power_kW, Avg_Duration_Min, Std_Dev_Min)
APPLIANCES = [
    ("Washer", 2.0, 45, 5),  # 45 min avg, varies by ~5 min
    ("Dryer", 3.0, 40, 5),
    ("Dishwasher", 1.5, 60, 2),
    ("EV", 5.0, 120, 10),
]


def appliance(env, name, power, avg_duration, std_dev, power_grid):
    # 1. Stochastic Start Delay
    # Randomly start between t=0 and t=10 minutes (Uniform distribution)
    start_delay = random.uniform(0, 10)
    yield env.timeout(start_delay)

    print(f"[{env.now:5.1f}m] {name} requests {power}kW")

    # 2. Request Power (Queueing happens here if grid is full)
    yield power_grid.get(power)

    # 3. Stochastic Duration
    # Use Gaussian (Normal) distribution for realistic process times
    actual_duration = random.gauss(avg_duration, std_dev)

    # Ensure duration is never negative
    actual_duration = max(1, actual_duration)

    print(f"[{env.now:5.1f}m] {name} START for {actual_duration:.1f}m")

    yield env.timeout(actual_duration)

    # 4. Return Power
    yield power_grid.put(power)
    print(f"[{env.now:5.1f}m] {name} END")


# # Setup the simulation
# env = simpy.Environment()
# grid = simpy.Container(env, capacity=MAX_POWER, init=MAX_POWER)

# # Initialize processes
# for name, power, avg_dur, std_dev in APPLIANCES:
#     env.process(appliance(env, name, power, avg_dur, std_dev, grid))

# # Run the simulation
# env.run()

import matplotlib.pyplot as plt


def run_monte_carlo(n_runs=10000):
    results = []

    for _ in range(n_runs):
        # 1. Setup a fresh environment for each run
        env = simpy.Environment()
        grid = simpy.Container(env, capacity=MAX_POWER, init=MAX_POWER)

        # 2. Register processes (using the 'appliance' function from Listing 8.6)
        for name, power, avg_dur, std_dev in APPLIANCES:
            env.process(appliance(env, name, power, avg_dur, std_dev, grid))

        # 3. Run until completion and store the final time
        env.run()
        results.append(env.now)

    # 4. Plotting
    plt.figure(figsize=(10, 6))
    plt.hist(results, bins=30, color="skyblue", edgecolor="black")

    # Add a line for the 95th percentile (The "Safe Bet")
    results.sort()
    p95 = results[int(0.95 * n_runs)]
    plt.axvline(p95, color="red", linestyle="dashed", linewidth=2)
    plt.text(p95 + 2, 300, f"95% Risk Limit: {p95:.0f} min", color="red")

    plt.title(f"Monte Carlo analysis at max {MAX_POWER} KW ({n_runs} Runs)")
    plt.xlabel("Time to complete all chores (minutes)")
    plt.ylabel("Frequency")
    plt.show()


# Run it
run_monte_carlo()
