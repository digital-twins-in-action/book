import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


# Define the Differential Equation (dy/dt = -0.5 * y)
def model(t, y):
    k = 0.5
    dydt = -k * y
    return dydt


plt.figure(figsize=(12, 7))

y_range = np.linspace(0, 5, 20)
t_range = np.linspace(0, 5, 20)
T, Y = np.meshgrid(t_range, y_range)
U = 1
V = -0.5 * Y
N = np.sqrt(U**2 + V**2)
U, V = U / N, V / N

plt.quiver(
    T,
    Y,
    U,
    V,
    color="gray",
    alpha=0.25,
    width=0.003,
    label="Vector Field (Differential Equation)",
)

t_eval = np.linspace(0, 5, 100)
for y_start in [1, 2, 3, 4, 5]:
    sol = solve_ivp(model, [0, 5], [y_start], t_eval=t_eval)
    plt.plot(
        sol.t,
        sol.y[0],
        "b--",
        alpha=0.3,
        label="General Solutions" if y_start == 1 else "",
    )

y0 = [4.2]
solution = solve_ivp(model, [0, 5], y0, t_eval=t_eval)

plt.plot(
    0,
    y0,
    "ro",
    markersize=12,
    label="Initial Value $y(t_0)=y_0$ (Sensor Data)",
    zorder=5,
)

plt.plot(
    solution.t,
    solution.y[0],
    "r-",
    linewidth=4,
    label="Unique Solution (Prediction)",
    zorder=4,
)

plt.xlabel("Time (t)", fontsize=20, fontweight="bold")
plt.ylabel("System State (y)", fontsize=20, fontweight="bold")

plt.xlim(0, 5)
plt.ylim(0, 5)
plt.tick_params(axis="both", labelsize=16)
plt.legend(fontsize=14, framealpha=0.9, loc="upper right")
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()
