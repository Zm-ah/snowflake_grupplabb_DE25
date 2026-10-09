import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

headers = {
    "Accept": "application/json",
    "Ocp-Apim-Subscription-Key": os.getenv("SWEDAVIA_API_KEY")
}

airports = [
    "ARN", "BMA", "GOT", "MMX", "LLA",
    "UME", "OSD", "VBY", "RNB", "KRN"
]

flight_date = "2026-10-07"

for airport in airports:
    for flight_type in ["arrivals", "departures"]:

        url = (
            f"https://api.swedavia.se/flightinfo/v2/"
            f"{airport}/{flight_type}/{flight_date}"
        )

        print("Request URL:", url)
        response = requests.get(url, headers=headers)

        print(f"{airport} {flight_type}: {response.status_code}")

        if response.ok:
            data = response.json()

            filename = (
                f"data/{flight_type}_{airport}_{flight_date}.json"
            )

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            print(f"Saved: {filename}")

        else:
            print(response.text)