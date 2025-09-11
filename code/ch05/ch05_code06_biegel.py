import requests
import json

# The base URL for the AAS API
BASE_URL = "https://v3-2.admin-shell-io.com"


def get_all_aas():
    """
    Retrieves and prints all available Asset Administration Shells from the API.
    """
    endpoint = f"{BASE_URL}/shells"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response
        aas_data = response.json()

        # Print the data in a readable format
        print("Successfully retrieved Asset Administration Shells:")
        print(json.dumps(aas_data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    get_all_aas()
