import requests

url = "http://127.0.0.1:5050/process_event"
data = {
    "event_id": 2
}

response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
print("Response JSON:", response.json())