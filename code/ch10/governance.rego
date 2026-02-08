package digital_twin.irrigation

import future.keywords.if

# Default to allowing operations
default allow_operation := true

# Governance Rule: Saturation Protection
# Block operation if we try to water an already wet lawn (moisture > 80%)
allow_operation := false if {
    input.command == "activate_zone"
    input.sensors.soil_moisture > 80
}
