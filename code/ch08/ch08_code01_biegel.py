import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Tank parameters
D_tank = 1.5  # Tank diameter (m)
R_tank = D_tank / 2  # Tank radius (m)
A_tank = np.pi * R_tank**2  # Tank cross-sectional area (m²)

# Leak/Orifice parameters
D_hole = 0.01  # Leak diameter (m) - 5 cm
R_hole = D_hole / 2  # Leak radius (m)
A_hole = np.pi * R_hole**2  # Leak area (m²)
g = 9.81  # Gravity (m/s²)

# Calculate leak coefficient
# k = (A_hole / A_tank) * sqrt(2 * g)
k = (A_hole / A_tank) * np.sqrt(2 * g)
print(f"Tank Area A_tank = {A_tank:.3f} m²")
print(f"Leak Area A_hole = {A_hole:.6f} m²")
print(f"Leak coefficient k = {k:.6f} m^0.5/s")


# Define the ODE
def leaking_tank(t, h):
    """
    ODE for water height in a leaking tank
    dh/dt = -k * sqrt(h)
    """
    if h <= 0:
        return 0  # No more water to leak
    return -k * np.sqrt(h)


# Initial conditions
h0 = 2.0  # Start with 3 meters of water

# Time span - let's see what happens over 1.5 hours
hours = 5
t_span = (0, hours * 3600)  # 0 to 1.5 hours in seconds
t_eval = np.linspace(0, hours * 3600, 1000)

# Solve the ODE
solution = solve_ivp(
    leaking_tank, t_span, [h0], t_eval=t_eval, method="RK45", dense_output=True
)

# Extract results
time_hours = solution.t / 3600  # Convert to hours
height = solution.y[0]

# Calculate theoretical empty time
# t_empty_theory = 2 * sqrt(h0) / k
t_empty_theory = 2 * np.sqrt(h0) / k / 3600  # in hours
print(f"\nTheoretical time to empty: {t_empty_theory:.2f} hours")

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(time_hours, height, label="Water Height Simulation")
plt.axhline(0, color="r", linestyle="--", label="Empty Tank")
plt.axvline(
    t_empty_theory,
    color="g",
    linestyle=":",
    label=f"Theoretical Empty Time ({t_empty_theory:.2f}h)",
)
plt.title("Time to drain rainwater tank")
plt.xlabel("Time (Hours)")
plt.ylabel("Water Height (m)")
plt.grid(True)
plt.legend()
plt.show()
