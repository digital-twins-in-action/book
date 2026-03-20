import numpy as np
from rdp import rdp
import matplotlib.pyplot as plt

time = np.linspace(0, 10, 1000)
data = np.sin(time * 2) + np.random.normal(0, 0.2, 1000)

points = np.column_stack((time, data))

EPSILON = 0.4
simplified_points = rdp(points, epsilon=EPSILON)

plt.figure(figsize=(12, 6))
plt.plot(time, data, label="Original Data", alpha=0.7)
plt.plot(
    simplified_points[:, 0],
    simplified_points[:, 1],
    "ro-",
    label=f"Simplified Data (epsilon={EPSILON})",
)
plt.title("Time Series Data Reduction using Ramer-Douglas-Peucker")
plt.xlabel("Time")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.show()

print(f"Original points: {len(points)}")
print(f"Simplified points: {len(simplified_points)}")
