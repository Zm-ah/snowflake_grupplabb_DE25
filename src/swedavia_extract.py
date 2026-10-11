import os
import json
import requests
from dotenv import load_dotenv
from datetime import date, timedelta


load_dotenv()

headers = {
    "Accept": "application/json",
    "Ocp-Apim-Subscription-Key": os.getenv("SWEDAVIA_API_KEY")
}

airports = [
    "ARN", "BMA", "GOT", "MMX", "LLA",
    "UME", "OSD", "VBY", "RNB", "KRN"
]

def get_last_days(days=3):
    today = date.today()
    return [
        (today - timedelta(days=i)).isoformat()
        for i in range(days)
    ]

os.makedirs("data", exist_ok=True)

# Delete old JSON files before extracting new data
for filename in os.listdir("data"):
    if filename.endswith(".json"):
        os.remove(os.path.join("data", filename))

print("Old JSON files deleted.")

for airport in airports:
    for flight_date in get_last_days(3):    
        for flight_type in ["arrivals", "departures"]:
            
            
            url = (
            f"https://api.swedavia.se/flightinfo/v2/"
            f"{airport}/{flight_type}/{flight_date}"
            )

            print("Request URL:", url)
            response = requests.get(url, headers=headers, timeout=30
            )
        
            print(
                f"{airport} {flight_type} {flight_date}: "
                f"{response.status_code}"
            )
            if response.ok:
                data = response.json()

                filename = (
                    f"data/{flight_type}_{airport}_{flight_date}.json"
                )

                with open(filename, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=2
                    )

                print(f"Saved: {filename}")

            else:
                print(response.text)