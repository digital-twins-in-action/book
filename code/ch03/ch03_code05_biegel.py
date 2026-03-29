import numpy as np
import matplotlib.pyplot as plt

TRUE_TEMP, STEPS, N = 22.0, 50, 5
np.random.seed(42)

noise_std = [0.3, 0.5, 0.8, 1.5, 0.4]
readings = [TRUE_TEMP + np.random.normal(0, s, STEPS) for s in noise_std]
readings[3][25:] += 2.0

x, P, Q = 20.0, 5.0, 0.01
R = [s**2 for s in noise_std]
estimates = []

for t in range(STEPS):
    P += Q
    for i in range(N):
        K = P / (P + R[i])
        x += K * (readings[i][t] - x)
        P *= 1 - K
    estimates.append(x)

avg = np.mean(readings, axis=0)

plt.figure(figsize=(16, 8))

colors = ["#aec7e8", "#c7b2d6", "#c9c9c9", "#f4a582", "#b5cfb5"]
for i in range(N):
    plt.plot(
        readings[i],
        alpha=0.6,
        color=colors[i],
        linewidth=1.5,
        label=f"Sensor {i+1} (s={noise_std[i]})",
    )

plt.plot(
    avg,
    linewidth=3.0,
    linestyle=(0, (4, 1.5, 1, 1.5)),
    color="#d95f02",
    label="Simple Average",
)
plt.plot(estimates, linewidth=3.0, color="#1b1b1b", label="Kalman Fusion")

plt.axhline(
    y=TRUE_TEMP,
    linestyle="--",
    linewidth=2.5,
    color="#1b7837",
    label="True Temperature",
)
plt.axvline(x=25, linestyle=":", linewidth=2, color="#636363", label="Sensor 4 drifts")

# plt.title(
#     "Sensor fusion: Kalman filter versus simple average",
#     fontsize=24,
#     fontweight="bold",
#     pad=20,
# )

plt.xlabel("Time step", fontsize=20, fontweight="bold")
plt.ylabel("Temperature (C)", fontsize=20, fontweight="bold")
plt.tick_params(axis="both", labelsize=16)

plt.legend(loc="upper left", fontsize=16, framealpha=0.9)
plt.tight_layout()
plt.show()
