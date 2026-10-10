import os
from datetime import date, timedelta

import dlt
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.swedavia.se/flightinfo/v2"
AIRPORTS = ["ARN", "BMA", "GOT", "MMX", "LLA", "UME", "OSD", "VBY", "RNB", "KRN"]
DIRECTIONS = ["arrivals", "departures"]


def _last_days(days=3):
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(days)]


def _get_flights(airport, flight_date, direction):
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv("SWEDAVIA_API_KEY"),
        "Accept": "application/json",
    }
    url = f"{BASE_URL}/{airport}/{direction}/{flight_date}"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get("flights", [])


@dlt.resource(
    name="flights",
    write_disposition="merge",
    primary_key=["flight_id", "airport", "flight_date", "direction"],
)
def flights_resource():
    for airport in AIRPORTS:
        for flight_date in _last_days():
            for direction in DIRECTIONS:
                flights = _get_flights(airport, flight_date, direction)
                print(airport, flight_date, direction, len(flights))

                for flight in flights:
                    flight["airport"] = airport
                    flight["flight_date"] = flight_date
                    flight["direction"] = direction

                yield flights

                