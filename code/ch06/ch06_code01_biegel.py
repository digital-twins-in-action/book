import numpy as np
from rdp import rdp
import matplotlib.pyplot as plt

time = np.linspace(0, 10, 1000)
data = np.sin(time * 2) + np.random.normal(0, 0.2, 1000)

points = np.column_stack((time, data))

EPSILON = 0.4
simplified_points = rdp(points, epsilon=EPSILON)

plt.figure(figsize=(16, 8))

plt.plot(time, data, label="Original Data", alpha=0.7, linewidth=2.5)

plt.plot(
    simplified_points[:, 0],
    simplified_points[:, 1],
    color="red",
    marker="o",
    linestyle="-",
    linewidth=3.0,
    markersize=10,
    label=f"Simplified Data (epsilon={EPSILON})",
)

plt.xlabel("Time", fontsize=20, fontweight="bold")
plt.ylabel("Value", fontsize=20, fontweight="bold")

plt.tick_params(axis="both", labelsize=16)

plt.legend(fontsize=16, framealpha=0.9)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"Original points: {len(points)}")
print(f"Simplified points: {len(simplified_points)}")
