import requests
import datetime
import time
import os
import json
import pandas as pd

# --- CONFIGURATION ---
ACCOUNT_ID = "REPLACE WITH_YOUR_ACCOUNT_ID"
DEVICE_ID = "REPLACE_WITH_YOUR_DEVICE_ID"
YEAR = 2025
OUTPUT_DIR = "electricity_raw"
FINAL_FILE = "home_energy_year_2025.csv"

# Replace this with the actual string from your browser
COOKIE_STRING = "JSESSIONID=..."

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cookie": COOKIE_STRING,
}

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def fetch_year_data():
    start_date = datetime.date(YEAR, 1, 1)
    # If today is in 2025, we stop at yesterday to avoid partial data
    today = datetime.date.today()
    end_date = min(datetime.date(YEAR, 12, 31), today - datetime.timedelta(days=1))

    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        next_day_str = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        url = f"https://selfserve.synergy.net.au/apps/rest/intervalData/{ACCOUNT_ID}/getHalfHourlyElecIntervalData"
        params = {
            "startDate": date_str,
            "endDate": next_day_str,
            "unbilledStartDate": next_day_str,
            "intervalDeviceIds": DEVICE_ID,
        }

        print(f"[{date_str}] Requesting data...")

        try:
            response = requests.get(url, headers=HEADERS, params=params)

            if response.status_code == 200:
                with open(os.path.join(OUTPUT_DIR, f"{date_str}.json"), "w") as f:
                    json.dump(response.json(), f)
            elif response.status_code == 401:
                print("!! Auth Failure: Your Cookie has expired. !!")
                break
            else:
                print(f"!! Error {response.status_code} for {date_str}")

        except Exception as e:
            print(f"!! Request failed for {date_str}: {e}")

        current_date += datetime.timedelta(days=1)
        time.sleep(1)  # Be kind to the Synergy portal


def compile_to_csv():
    """Reads all JSON files and creates a time-series CSV for Chapter 9."""
    all_records = []

    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if filename.endswith(".json"):
            with open(os.path.join(OUTPUT_DIR, filename), "r") as f:
                day_data = json.load(f)
                # Note: The Synergy JSON structure usually has a list under 'intervalData'
                # and each entry has 'intervalDatetime' and 'consumption'
                if "intervalData" in day_data:
                    all_records.extend(day_data["intervalData"])

    if all_records:
        df = pd.DataFrame(all_records)
        # Ensure date columns are proper datetime objects
        df["intervalDatetime"] = pd.to_datetime(df["intervalDatetime"])
        df.sort_values("intervalDatetime", inplace=True)
        df.to_csv(FINAL_FILE, index=False)
        print(f"--- SUCCESS: {FINAL_FILE} created with {len(df)} intervals ---")


if __name__ == "__main__":
    fetch_year_data()
    compile_to_csv()
