import requests

AGENT = "http://localhost:8180/v1"

post = lambda path, payload: requests.post(f"{AGENT}/{path}", json=payload).json()

# Load a simple Cedar policy
post("policies", {
    "id": "twin-policy-01",
    "content": """
    permit(
      principal == User::"maintenance_bot",
      action == Action::"update_state",
      resource == Twin::"hvac_unit_1"
    );
    """
})

# Authorization check
decision = post("is_authorized", {
    "principal": 'User::"maintenance_bot"',
    "action": 'Action::"update_state"',
    "resource": 'Twin::"hvac_unit_1"',
    "context": {}
}).get("decision")

print(f"Digital Twin Access Decision: {decision}")
