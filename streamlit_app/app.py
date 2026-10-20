# Home page: key numbers for the latest three days in the data
import streamlit as st

from db import LAST_3_DAYS, run_query

st.set_page_config(page_title="Flight Punctuality", layout="wide")
st.title("Flight Punctuality")

df = run_query(f"""
    SELECT
        COUNT(*) AS TOTAL_FLIGHTS,
        SUM(CASE WHEN IS_DELETED THEN 1 ELSE 0 END) AS DELETED_FLIGHTS,
        SUM(CASE WHEN HAS_ACTUAL_TIME THEN 1 ELSE 0 END) AS OPERATED_FLIGHTS,
        SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        SUM(CASE WHEN IS_CANCELLED THEN 1 ELSE 0 END) AS CANCELLED_FLIGHTS,
        MIN(FLIGHT_DATE) AS FIRST_DATE,
        MAX(FLIGHT_DATE) AS LAST_DATE
    FROM FCT_FLIGHTS
    WHERE {LAST_3_DAYS}
""")

total = int(df["TOTAL_FLIGHTS"][0])
deleted = int(df["DELETED_FLIGHTS"][0])
operated = int(df["OPERATED_FLIGHTS"][0])
delayed = int(df["DELAYED_FLIGHTS"][0])
cancelled = int(df["CANCELLED_FLIGHTS"][0])
scheduled = total - deleted  # flights that were actually in the schedule
first_date = df["FIRST_DATE"][0]
last_date = df["LAST_DATE"][0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Scheduled flights", scheduled)
col2.metric("Operated flights", operated)
col3.metric("Delayed (of operated)", f"{delayed} ({delayed / operated:.1%})")
col4.metric("Cancelled (of scheduled)", f"{cancelled} ({cancelled / scheduled:.1%})")

st.caption(
    f"Data from Swedavia airports, {first_date} to {last_date} (latest three days). "
    "Delayed = more than 15 minutes after scheduled time. "
    "Deleted entries (removed from the schedule) are excluded."
)