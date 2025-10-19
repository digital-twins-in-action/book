import requests
import json

API_KEY = ""


def query_knowledge_graph(query_text):
    if API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Please replace 'YOUR_API_KEY_HERE' with a valid Google API Key.")
        return

    url = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        "query": query_text,
        "key": API_KEY,
        "limit": 1,
        "indent": True,
    }

    try:
        print(f"Searching for: '{query_text}'...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)

        if data.get("itemListElement"):
            top_result = data["itemListElement"][0]["result"]
            name = top_result.get("name", "N/A")
            description = top_result.get("description", "No description available.")
            detailed_description = top_result.get("detailedDescription", {}).get(
                "articleBody", "N/A"
            )
            url = top_result.get("url", "N/A")

            print("\n--- Top Knowledge Graph Result ---")
            print(f"Entity Name: {name}")
            print(f"Type: {description}")
            print(f"Description:\n{detailed_description}")
            print(f"URL: {url}")
            print("----------------------------------")
        else:
            print(f"No results found for '{query_text}'.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from the API.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    query_to_search = "Lake Kariba"
    query_knowledge_graph(query_to_search)
