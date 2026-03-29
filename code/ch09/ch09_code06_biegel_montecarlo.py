import simpy
import random
import matplotlib.pyplot as plt

# Fixed constants
MAX_POWER = 7.0
APPLIANCES = [
    ("Washer", 2.0, 45, 5),
    ("Dryer", 3.0, 40, 5),
    ("Dishwasher", 1.5, 60, 2),
    ("EV", 5.0, 120, 10),
]


def appliance(env, name, power, avg_duration, std_dev, power_grid):
    start_delay = random.uniform(0, 10)
    yield env.timeout(start_delay)
    yield power_grid.get(power)
    actual_duration = max(1, random.gauss(avg_duration, std_dev))
    yield env.timeout(actual_duration)
    yield power_grid.put(power)


def run_monte_carlo(n_runs=10000):
    results = []

    for _ in range(n_runs):
        env = simpy.Environment()
        grid = simpy.Container(env, capacity=MAX_POWER, init=MAX_POWER)
        for name, power, avg_dur, std_dev in APPLIANCES:
            env.process(appliance(env, name, power, avg_dur, std_dev, grid))
        env.run()
        results.append(env.now)

    plt.figure(figsize=(12, 7))
    plt.hist(results, bins=30, color="skyblue", edgecolor="black", alpha=0.7)

    results.sort()
    p95 = results[int(0.95 * n_runs)]

    plt.axvline(p95, color="red", linestyle="dashed", linewidth=4)

    plt.text(
        p95 + 2,
        plt.gca().get_ylim()[1] * 0.7,
        f"95% Risk Limit: {p95:.0f} min",
        color="red",
        fontsize=16,
        fontweight="bold",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
    )

    plt.title(
        f"Monte Carlo analysis at max {MAX_POWER} KW ({n_runs} Runs)",
        fontsize=24,
        fontweight="bold",
        pad=20,
    )
    plt.xlabel("Time to complete all chores (minutes)", fontsize=20, fontweight="bold")
    plt.ylabel("Frequency", fontsize=20, fontweight="bold")

    plt.tick_params(axis="both", labelsize=16)
    plt.grid(axis="y", linestyle=":", alpha=0.6)

    plt.tight_layout()

    plt.show()


# Run it
if __name__ == "__main__":
    run_monte_carlo()
