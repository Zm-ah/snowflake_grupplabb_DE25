# Shared database helper used by all pages
import os

from dotenv import load_dotenv
import pandas as pd
import snowflake.connector
import streamlit as st

load_dotenv()


# SQL condition that keeps only the latest complete days, 
# today is excluded because its flights are not finished yet
LAST_3_DAYS = """
    FLIGHT_DATE < CURRENT_DATE()
    AND FLIGHT_DATE >= (
        SELECT DATEADD('day', -2, MAX(FLIGHT_DATE))
        FROM FCT_FLIGHTS
        WHERE FLIGHT_DATE < CURRENT_DATE()
    )
"""


def _snowflake_config() -> dict:
    """Read Snowflake settings from environment variables (Docker/Azure),
    otherwise from .streamlit/secrets.toml (local development)."""
    if "SNOWFLAKE_ACCOUNT" in os.environ:
        return {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user": os.environ["SNOWFLAKE_USER"],
            "password": os.environ["SNOWFLAKE_PASSWORD"],
            "role": os.environ["SNOWFLAKE_ROLE"],
            "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
            "database": os.environ["SNOWFLAKE_DATABASE"],
            "schema": os.environ["SNOWFLAKE_SCHEMA"],
        }
    return dict(st.secrets["snowflake"])


@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    """Run a SQL query in Snowflake and return the result as a DataFrame."""
    # TIMEZONE makes CURRENT_DATE() follow Swedish time instead of Snowflake's default
    conn = snowflake.connector.connect(
        **_snowflake_config(),
        session_parameters={"TIMEZONE": "Europe/Stockholm"},
    )
    try:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [col[0] for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        conn.close()