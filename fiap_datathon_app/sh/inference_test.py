import requests
import json

URL = "http://127.0.0.1:8000/recommendation/"
API_KEY = "your_default_api_token"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "viewed_news": [
        "c8aab885-433d-4e46-8066-479f40ba7fb2",
        "68d2039c-c9aa-456c-ac33-9b2e8677fba7",
        "13e423ce-1d69-4c78-bc18-e8c8f7271964",
    ],
    "init_time": "2020-12-31T00:00:00Z",
    "end_time": "2026-12-31T00:00:00Z"
    ,"top_n": 2
    ,"news_text": True
}

try:
    response = requests.post(URL, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    print(json.dumps(response.json()))  # Print the JSON response
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError:
    print("Response is not valid JSON")
    print(response.text)