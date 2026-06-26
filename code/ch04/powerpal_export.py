import os
import requests
import csv
from datetime import datetime, timedelta

# Powerpal API Endpoint
API_URL = "https://readings.powerpal.net/api/v1/device/{device_serial}"

def get_powerpal_data(device_serial, api_token, start_timestamp, end_timestamp):
    """Fetches reading data from the Powerpal API."""
    url = API_URL.format(device_serial=device_serial)
    
    headers = {
        "Authorization": api_token,
        "Accept": "application/json"
    }
    
    # The API expects UNIX timestamps
    params = {
        "start": int(start_timestamp),
        "end": int(end_timestamp)
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() # Raise an error if the request fails
    return response.json()

if __name__ == "__main__":
    # Read authentication details from environment variables (or replace with your strings)
    DEVICE_SERIAL = os.getenv("POWERPAL_DEVICE_SERIAL", "your_device_serial")
    API_TOKEN = os.getenv("POWERPAL_API_TOKEN", "your_api_token")
    
    if DEVICE_SERIAL == "your_device_serial" or API_TOKEN == "your_api_token":
        print("Please set your POWERPAL_DEVICE_SERIAL and POWERPAL_API_TOKEN environment variables.")
        print("Example: export POWERPAL_DEVICE_SERIAL='123456'")
        exit(1)
        
    # Example: Fetch data for the last 2 hours (similar to the go repo's powerpal2csv default)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)
    
    print(f"Fetching data from {start_time.strftime('%Y-%m-%d %H:%M:%S')} "
          f"to {end_time.strftime('%Y-%m-%d %H:%M:%S')}...")
    
    try:
        data = get_powerpal_data(
            DEVICE_SERIAL, 
            API_TOKEN, 
            start_time.timestamp(), 
            end_time.timestamp()
        )
        
        print(f"Retrieved {len(data)} new readings.")
        
        # Export to CSV
        if data and isinstance(data, list):
            filename = f"powerpal_export_{int(end_time.timestamp())}.csv"
            with open(filename, mode='w', newline='') as file:
                # Use the keys from the first JSON object as CSV headers
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"Data successfully saved to {filename}")
        else:
            print("No data returned for this time period.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
