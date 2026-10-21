# Shared database helper used by all pages
import pandas as pd
import snowflake.connector
import streamlit as st


# SQL condition that keeps only the latest complete days:
# today is excluded because its flights are not finished yet
LAST_3_DAYS = """
    FLIGHT_DATE < CURRENT_DATE()
    AND FLIGHT_DATE >= (
        SELECT DATEADD('day', -2, MAX(FLIGHT_DATE))
        FROM FCT_FLIGHTS
        WHERE FLIGHT_DATE < CURRENT_DATE()
    )
"""



@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    """Run a SQL query in Snowflake and return the result as a DataFrame."""
    conn = snowflake.connector.connect(**st.secrets["snowflake"])
    try:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [col[0] for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        conn.close()