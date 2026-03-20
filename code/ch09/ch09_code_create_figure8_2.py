import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


# 1. Define the Differential Equation (dy/dt = -0.5 * y)
# NOTE: solve_ivp requires the signature f(t, y), unlike odeint's f(y, t)
def model(t, y):
    k = 0.5
    dydt = -k * y
    return dydt


# 2. Setup the Plot
plt.figure(figsize=(10, 6))
plt.title("The Initial Value Problem\u2014from general physics to specific prediction")
plt.xlabel("Time (t)")
plt.ylabel("System State (y)")
plt.xlim(0, 5)
plt.ylim(0, 5)

# 3. Draw the Vector Field (The Physics / The Rules)
# This visualizes the differential equation everywhere
y_range = np.linspace(0, 5, 20)
t_range = np.linspace(0, 5, 20)
T, Y = np.meshgrid(t_range, y_range)
# We calculate the vector components manually for the grid
U = 1  # The change in time is constant
V = -0.5 * Y  # The change in Y depends on the equation
# Normalize arrows for cleaner look
N = np.sqrt(U**2 + V**2)
U, V = U / N, V / N
plt.quiver(
    T,
    Y,
    U,
    V,
    color="gray",
    alpha=0.3,
    width=0.003,
    label="Vector Field (Differential Equation)",
)

# 4. Draw General Solutions (Possible Futures)
t_eval = np.linspace(0, 5, 100)
for y_start in [1, 2, 3, 4, 5]:
    # solve_ivp returns a result object. We access result.y[0] for the values.
    sol = solve_ivp(model, [0, 5], [y_start], t_eval=t_eval)
    plt.plot(
        sol.t,
        sol.y[0],
        "b--",
        alpha=0.3,
        label="General Solutions" if y_start == 1 else "",
    )

# 5. Draw the Initial Value Problem (The Digital Twin Prediction)
# Specific Initial Condition: y(0) = 4.2
y0 = [4.2]
solution = solve_ivp(model, [0, 5], y0, t_eval=t_eval)

# Plot the Initial Point (Sensor Reading)
plt.plot(
    0,
    y0,
    "ro",
    markersize=10,
    label="Initial Value $y(t_0)=y_0$ (Sensor Data)",
    zorder=5,
)
# Plot the Specific Solution (Prediction)
plt.plot(
    solution.t,
    solution.y[0],
    "r-",
    linewidth=3,
    label="Unique Solution (Prediction)",
    zorder=4,
)

plt.legend(loc="upper right")
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()
