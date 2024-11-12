import requests
import json

test_data = {
    "email": "maya.oberholzer@outlook.com",  # Using the same email from .env
    "name": "Test User",
    "videoUrl": "https://example.com/test-video"  # Test video URL
}

response = requests.post(
    'http://localhost:8000/send-email',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(test_data)
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
