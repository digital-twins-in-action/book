import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Tank parameters
D_tank = 1.5
R_tank = D_tank / 2
A_tank = np.pi * R_tank**2

# Leak/Orifice parameters
D_hole = 0.01
R_hole = D_hole / 2
A_hole = np.pi * R_hole**2
g = 9.81

# Calculate leak coefficient
k = (A_hole / A_tank) * np.sqrt(2 * g)


# Define the ODE
def leaking_tank(t, h):
    if h <= 0:
        return 0
    return -k * np.sqrt(h)


# Initial conditions
h0 = 2.0
hours = 5
t_span = (0, hours * 3600)
t_eval = np.linspace(0, hours * 3600, 1000)

# Solve the ODE
solution = solve_ivp(
    leaking_tank, t_span, [h0], t_eval=t_eval, method="RK45", dense_output=True
)

# Extract results
time_hours = solution.t / 3600
height = solution.y[0]
t_empty_theory = 2 * np.sqrt(h0) / k / 3600

plt.figure(figsize=(12, 7))

plt.plot(
    time_hours, height, label="Water Height Simulation", linewidth=3, color="tab:blue"
)

plt.axhline(0, color="r", linestyle="--", linewidth=2, label="Empty Tank")

plt.axvline(
    t_empty_theory,
    color="g",
    linestyle=":",
    linewidth=3,
    label=f"Theoretical Empty Time ({t_empty_theory:.2f}h)",
)

plt.title(
    "Time to drain rainwater tank",
    fontsize=24,
    fontweight="bold",
    pad=20,
)
plt.xlabel("Time (Hours)", fontsize=20, fontweight="bold")
plt.ylabel("Water Height (m)", fontsize=20, fontweight="bold")

# Formatting ticks and legend
plt.tick_params(axis="both", labelsize=16)
plt.legend(fontsize=14, framealpha=0.9, loc="upper right")
plt.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.show()
