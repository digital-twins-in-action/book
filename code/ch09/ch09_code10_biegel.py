import requests
from typing import Dict, Any
from strands import tool


@tool
def get_realtime_solar_data(scope: str = "System") -> Dict[str, Any]:
    """
    Fetches real-time solar production metrics from the local Fronius inverter.

    Use this tool when you need to know the current solar output (PAC) or
    the total energy produced today (DAY_ENERGY).

    Args:
        scope: The data scope to query. Defaults to "System".

    Returns:
        Dict[str, Any]: A dictionary containing:
            - current_power_w: Current AC power output in Watts.
            - day_energy_wh: Total energy produced today in Watt-hours.
            - timestamp: The time of the reading.
    """
    url = "http://192.168.1.180/solar_api/v1/GetInverterRealtimeData.cgi"

    try:
        response = requests.get(url, params={"Scope": scope}, timeout=5)
        response.raise_for_status()
        data = response.json()

        realtime_data = data.get("Body", {}).get("Data", {})

        pac_value = realtime_data.get("PAC", {}).get("Values", {}).get("1", 0)
        day_energy = realtime_data.get("DAY_ENERGY", {}).get("Values", {}).get("1", 0)

        return {
            "current_power_w": pac_value,
            "day_energy_wh": day_energy,
            "timestamp": data.get("Head", {}).get("Timestamp"),
            "status": "success",
        }

    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to connect to inverter: {str(e)}",
        }
