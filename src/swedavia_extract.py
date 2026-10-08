import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

headers = {
    "Accept": "application/json",
    "Ocp-Apim-Subscription-Key": os.getenv("SWEDAVIA_API_KEY")
}

# Arrivals
url = "https://api.swedavia.se/flightinfo/v2/ARN/arrivals/2026-10-07"
response = requests.get(url, headers=headers)

print("Arrivals:", response.status_code)

arrivals_data = response.json()

with open("data/arrivals_ARN_2026-10-06.json", "w", encoding="utf-8") as file:
    json.dump(arrivals_data, file, ensure_ascii=False, indent=2)


# Departures
url = "https://api.swedavia.se/flightinfo/v2/ARN/departures/2026-10-07"
response = requests.get(url, headers=headers)

print("Departures:", response.status_code)

departures_data = response.json()

with open("data/departures_ARN_2026-10-06.json", "w", encoding="utf-8") as file:
    json.dump(departures_data, file, ensure_ascii=False, indent=2)