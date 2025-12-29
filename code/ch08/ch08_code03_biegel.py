import numpy as np
from fmpy import simulate_fmu

start_values = {"tank.level_start": 2}

output_variables = ["tank.level"]

result = simulate_fmu(
    "WaterTankDrainage.fmu",
    stop_time=15000,
    start_values=start_values,
    output=output_variables,
)

print(result)
