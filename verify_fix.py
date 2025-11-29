import requests
import json

try:
    response = requests.post(
        "http://localhost:8000/api/verify",
        json={
            "text": "5G towers spread coronavirus",
            "audience_level": "general"
        }
    )
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
