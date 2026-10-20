# Home page: key numbers for the whole dataset
import streamlit as st

from db import run_query

st.set_page_config(page_title="Flight Punctuality", layout="wide")
st.title("Flight Punctuality")

df = run_query("""
    SELECT
        COUNT(*) AS TOTAL_FLIGHTS,
        SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        SUM(CASE WHEN IS_CANCELLED THEN 1 ELSE 0 END) AS CANCELLED_FLIGHTS
    FROM FCT_FLIGHTS
""")

total = int(df["TOTAL_FLIGHTS"][0])
delayed = int(df["DELAYED_FLIGHTS"][0])
cancelled = int(df["CANCELLED_FLIGHTS"][0])

col1, col2, col3 = st.columns(3)
col1.metric("Total flights", total)
col2.metric("Delayed flights", f"{delayed} ({delayed / total:.1%})")
col3.metric("Cancelled flights", f"{cancelled} ({cancelled / total:.1%})")