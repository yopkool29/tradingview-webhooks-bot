import requests
import json

# Configuration
url = "http://localhost:5000/webhook"

key = "WebhookReceivedMtFlatten:695f2a"

# Payload de test
payload = {
    "key": key,
    "symbol": "XAUUSD",
    "magic": 202220001,
}

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
