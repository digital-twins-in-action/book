import requests
from typing import Dict, Any
from datetime import datetime
from strands import Agent, tool
from ch09_code10_biegel import get_realtime_solar_data


@tool
def get_weather_forecast() -> Dict[str, Any]:
    """
    Fetches the current weather and 24-hour forecast for the home location (Perth).

    Use this tool to get:
    1. Current cloud cover (%) and temperature (C).
    2. Hourly forecast for temperature, cloud cover, and direct solar radiation.

    Returns:
        Dict[str, Any]: Structured weather data containing:
            - current: {temperature_c, cloud_cover_pct, time}
            - hourly_forecast: List of dictionaries, each representing one hour
              with keys: time, temp_c, cloud_cover_pct, solar_radiation_w_m2.
    """
    # Hardcoded URL for the home digital twin location (Perth)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=-31.9522&longitude=115.8614"
        "&hourly=temperature_2m,cloud_cover,direct_radiation"
        "&current=cloud_cover,temperature_2m"
        "&timezone=Asia%2FSingapore&forecast_days=1"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # 1. Parse Current Conditions
        current_raw = data.get("current", {})
        current_weather = {
            "temperature_c": current_raw.get("temperature_2m"),
            "cloud_cover_pct": current_raw.get("cloud_cover"),
            "time": current_raw.get("time"),
        }

        # 2. Parse and Restructure Hourly Forecast
        # The API returns lists: {"time": [t1, t2], "temp": [v1, v2]}
        # We convert this to: [{"time": t1, "temp": v1}, {"time": t2, "temp": v2}]
        hourly_raw = data.get("hourly", {})
        times = hourly_raw.get("time", [])
        temps = hourly_raw.get("temperature_2m", [])
        clouds = hourly_raw.get("cloud_cover", [])
        radiation = hourly_raw.get("direct_radiation", [])

        forecast_list = []

        # Zip the lists together to create row-based records
        # Using min() ensures we don't crash if lists are uneven lengths
        count = min(len(times), len(temps), len(clouds), len(radiation))

        for i in range(count):
            forecast_list.append(
                {
                    "time": times[i],
                    "temp_c": temps[i],
                    "cloud_cover_pct": clouds[i],
                    "solar_radiation_w_m2": radiation[i],
                }
            )

        return {
            "status": "success",
            "location": "Perth",
            "current": current_weather,
            "hourly_forecast": forecast_list,
        }

    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Weather API connection failed: {str(e)}",
        }


@tool
def get_space_climate_history(
    start_date: str, end_date: str, space_name: str = "Bedroom 1"
) -> Dict[str, Any]:
    """
    Queries the Digital Twin's GraphQL API to retrieve temperature and humidity
    sensor history for a specific room.

    Args:
        start_date: ISO 8601 string (UTC).
        end_date: ISO 8601 string (UTC).
        space_name: The name of the room (e.g., "Bedroom 1", "Kitchen").

    Returns:
        Dict[str, Any]: A dictionary with keys 'temperature' and 'humidity',
        each containing a list of {timestamp, value} records.
    """
    url = "http://127.0.0.1:5050/graphql"

    print("getting space climate history")

    # 2. Construct the GraphQL Query with Variables
    # Using variables prevents injection and makes the query cleaner
    query = """
    query GetSensorsInSpace($space: String!, $startDate: String!, $endDate: String!) {
      spaces(space: $space, startDate: $startDate, endDate: $endDate) {
        name
        measurements {
          name
          values {
            timestamp
            value
          }
        }
      }
    }
    """

    variables = {"space": space_name, "startDate": start_date, "endDate": end_date}

    try:
        response = requests.post(
            url, json={"query": query, "variables": variables}, timeout=5
        )
        print(response.json())
        response.raise_for_status()
        result = response.json()

        # 3. Parse and Simplify Response
        # The raw GraphQL structure is deep: data -> spaces[0] -> measurements[]
        # We flatten this for the LLM to read easily.
        data = result.get("spaces", [])

        if not data:
            print("Error")
            return {
                "status": "error",
                "message": f"No data found for space: {space_name}",
            }

        measurements = data[0].get("measurements", [])

        # Structure the output by sensor type
        output = {
            "space": space_name,
            "period": {"start": start_date, "end": end_date},
            "humidity": [],
            "temperature": [],
        }

        for m in measurements:
            m_name = m.get("name")
            if m_name in output:
                output[m_name] = m.get("values", [])

        # Optional: Add simple stats to help the LLM summarize without processing all rows
        # (e.g., "Max temp was 27.18C")
        if output["temperature"]:
            temps = [x["value"] for x in output["temperature"]]
            output["stats"] = {
                "max_temp": max(temps),
                "min_temp": min(temps),
                "avg_temp": round(sum(temps) / len(temps), 2),
            }

        return output

    except requests.RequestException as e:
        return {"status": "error", "message": f"GraphQL query failed: {str(e)}"}


@tool
def set_aircon_state(power: str, target_temp: float):
    """
    Sends command to the Home Digital Twin to change AC state.
    power: 'ON' or 'OFF'
    """
    return f"SUCCESS: AC set to {power} with target {target_temp}°C"


current_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

system_prompt = f"""
### ROLE
Climate Control Agent. Current Time: {current_time_str}.

### CONSTANTS
- **Target Temp:** 21°C–24°C
- **AC Load:** 1500W
- **Baseload:** 1000W (08:00–16:00); 200W (otherwise).

### CONTROL POLICY
1. **Fetch Data:** Get current solar ($P_{{solar}}$), forecast, and indoor temp ($T_{{room}}$ (last 24 hours).
2. **Calculate Excess:** $P_{{excess}} = P_{{solar}} - \\text{{Baseload}}$.
3. **Evaluate State:**
   - **COOLING NEEDED** if $T_{{room}} > 24°C$.
   - **OPPORTUNISTIC COOLING** if $P_{{excess}} > 1500W$ AND $T_{{room}} > 21°C$ (Priority: Solar).
   - **IDLE** otherwise.
4. **Safety:** Apply hysteresis (don't cycle AC if state changed <15 mins ago).
5. **Priorities:** Always prioritize minimizing grid consumption over comfort.

### OUTPUT INSTRUCTION
Output a concise reasoning step (e.g., "Excess solar 1600W > AC Load; engaging cooling."), then call `set_aircon_state` if a change is needed.
"""


agent = Agent(
    name="ClimateAgent",
    system_prompt=system_prompt,
    tools=[
        get_realtime_solar_data,
        get_weather_forecast,
        get_space_climate_history,
        set_aircon_state,
    ],
)

if __name__ == "__main__":
    user_q = "Check the status of the Lounge and Bedroom 1 and make sure its at a comfortable temperature"
    print(f"User: {user_q}")
    response = agent(user_q)
    print(f"Agent: {response}")
