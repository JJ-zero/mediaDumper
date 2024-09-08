from requests import post

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyZWZlZTUyY2UxNmU0ODQyYmRlYzE5MjJmMDJlZGRjOCIsImlhdCI6MTcyNTgxNzkyMCwiZXhwIjoyMDQxMTc3OTIwfQ.EZRG-ygeuBVqo9dNBhNLgDKNg5t83yZUGXQMUBpMqoA"

url = "http://localhost:8123/api/services/notify/mobile_app_fusion"
headers = {"Authorization": f"Bearer {TOKEN}"}
data = {"message": "This?"}

response = post(url, headers=headers, json=data)
print(response.text)