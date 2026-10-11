import string
import time
from io import StringIO

import dlt
import pandas as pd
import requests

HEADERS = {"User-Agent": "student-data-engineering-project/1.0"}


def _get_tables(url):
    print("Hämtar", url)
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return pd.read_html(StringIO(response.text))


def _clean(df):
    df.columns = (
        df.columns.str.replace("\xa0", " ")
        .str.replace(r"\[.*?\]", "", regex=True)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    for col in df.select_dtypes(exclude="number").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"\[.*?\]", "", regex=True)
            .str.replace("\xa0", " ")
            .str.replace("*", "", regex=False)
            .str.strip()
        )
        df[col] = df[col].mask(df[col].isin(["nan", "None", ""]))
    return df


def _to_records(df):
    return df.astype(object).where(df.notna(), None).to_dict(orient="records")


@dlt.resource(name="airports", write_disposition="replace")
def airports_resource():
    url = "https://en.wikipedia.org/wiki/List_of_airports_in_Sweden"
    table = next(t for t in _get_tables(url) if "IATA" in t.columns).copy()
    airports = _clean(table).rename(columns={"runway_s": "runways"})
    airports["passengers_2023"] = pd.to_numeric(airports["passengers_2023"], errors="coerce")
    yield _to_records(airports)


@dlt.resource(name="airlines", write_disposition="replace")
def airlines_resource():
    frames = []
    for letter in string.ascii_uppercase:
        url = f"https://en.wikipedia.org/wiki/List_of_airline_codes_({letter})"
        frames += [t for t in _get_tables(url) if "IATA" in t.columns]
        time.sleep(0.5)
    airlines = _clean(pd.concat(frames, ignore_index=True)).drop_duplicates()
    yield _to_records(airlines) 
    