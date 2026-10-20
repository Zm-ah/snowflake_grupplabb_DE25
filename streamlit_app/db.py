# Shared database helper used by all pages
import pandas as pd
import snowflake.connector
import streamlit as st


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