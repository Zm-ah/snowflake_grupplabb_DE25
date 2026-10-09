import os
from dotenv import load_dotenv
from datetime import date, timedelta
import requests
import dlt

load_dotenv()

api_key = os.getenv("SWEDAVIA_API_KEY")

if api_key is None:
    raise ValueError("SWEDAVIA_API_KEY saknas i .env")

print("Nyckeln hittades, längd:", len(api_key)) 




AIRPORTS = ["ARN", "BMA", "GOT", "MMX", "LLA", "UME", "OSD", "VBY", "RNB", "KRN"]

today = date.today()
dates = [(today - timedelta(days=i)).isoformat() for i in range(3)]

print("Flygplatser:", AIRPORTS)
print("Datum:", dates)




BASE_URL = "https://api.swedavia.se/flightinfo/v2"
HEADERS = {
    "Ocp-Apim-Subscription-Key": api_key,
    "Accept": "application/json",
}


def fetch_flights(airport, flight_date, direction):
    url = f"{BASE_URL}/{airport}/{direction}/{flight_date}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("flights", [])





@dlt.resource(
    name="flights",
    write_disposition="merge",
    primary_key=["flight_id", "airport", "flight_date", "direction"],
)
def flights_resource():
    for airport in AIRPORTS:
        for flight_date in dates:
            for direction in ["arrivals", "departures"]:
                flights = fetch_flights(airport, flight_date, direction)

                for flight in flights:
                    flight["airport"] = airport
                    flight["flight_date"] = flight_date
                    flight["direction"] = direction

                print(airport, flight_date, direction, len(flights))
                yield flights


pipeline = dlt.pipeline(
    pipeline_name="swedavia_flights",
    destination="snowflake",
    dataset_name="staging",
)

if __name__ == "__main__":
    info = pipeline.run(flights_resource())
    print(info) 