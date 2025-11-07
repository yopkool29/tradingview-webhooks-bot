import requests
import json

# Configuration
url = "http://localhost:5000/webhook"

key = "WebhookReceivedMtOrder:0ea2fe"

# Payload de test
payload = {
    "key": key,
    "symbol": "XAUUSD",
    "magic": 202220001,
    "order_type": "sell",
    "volume": 0.1,
    "tp_rel": 1000, # 1000 points
    "sl_rel": 500 # 500 points
}

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
