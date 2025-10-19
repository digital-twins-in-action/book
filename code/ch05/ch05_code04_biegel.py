import numpy as np
import matplotlib.pyplot as plt

# 1. Define the physical system and its constants
T_ambient = 5.0  # Constant outside ambient temperature ($^\circ C$)
C_air = 100.0  # Thermal capacitance of the room's air ($J/^\circ C$)
R_wall = 1.0  # Thermal resistance of the walls ($^\circ C \cdot s / J$)


# 2. Define the physics model (the differential equation)
def room_thermal_model(T_room):
    heat_transfer_walls = (T_ambient - T_room) / R_wall
    dT_room_dt = heat_transfer_walls / C_air
    return dT_room_dt


# 3. Simulate the model over time
initial_temp = 10.0  # Start with a room temperature of 10°C
dt = 0.1  # Time step size (seconds)
t_end = 700.0  # Total simulation time (seconds)
time = np.arange(0, t_end, dt)

temp_history = [initial_temp]

for t in time[1:]:
    current_temp = temp_history[-1]
    next_temp = current_temp + room_thermal_model(current_temp) * dt
    temp_history.append(next_temp)

# 4. Visualize the results
plt.figure(figsize=(10, 6))
plt.plot(time, temp_history, "b-", label="Room Temperature")
plt.axhline(y=T_ambient, color="gray", linestyle="--", label="Ambient Temperature")
plt.xlabel("Time (s)")
plt.ylabel("Temperature")
plt.title("Room Temperature Model")  # Changed title here
plt.grid(True)
plt.legend()

plt.show()
