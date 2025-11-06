import requests
import json

# Configuration
url = "http://localhost:5000/webhook"

key = "WebhookReceived:253f3e"

# Payload de test
payload = {
    "key": key,
    "message": "Nice, I'm a webhook from Python!",
    "data": "XAUUSD"
}

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
