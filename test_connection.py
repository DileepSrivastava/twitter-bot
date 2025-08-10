import requests

try:
    response = requests.get('https://api.twitter.com/')
    print("Status code:", response.status_code)
except Exception as e:
    print("Error:", e)