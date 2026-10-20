
import streamlit as st

from db import LAST_3_DAYS, run_query

st.title("✈️ Airline Performance")
st.caption("Flight punctuality · Latest three data days")

df = run_query(f"""
    SELECT
        a.AIRLINE_NAME,
        COUNT(*) AS TOTAL_FLIGHTS,
        SUM(CASE WHEN f.IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        SUM(CASE WHEN f.IS_CANCELLED THEN 1 ELSE 0 END) AS CANCELLED_FLIGHTS
    FROM FCT_FLIGHTS f
    JOIN DIM_AIRLINE a
        ON f.AIRLINE_KEY = a.AIRLINE_KEY
    WHERE {LAST_3_DAYS}
      AND f.IS_DELETED = FALSE
    GROUP BY a.AIRLINE_NAME
    ORDER BY TOTAL_FLIGHTS DESC
""")

total_flights = int(df["TOTAL_FLIGHTS"].sum())
total_delayed = int(df["DELAYED_FLIGHTS"].sum())
total_cancelled = int(df["CANCELLED_FLIGHTS"].sum())
airline_count = len(df)

delay_rate = total_delayed / total_flights if total_flights else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total flights", f"{total_flights:,}")
col2.metric("Airlines", airline_count)
col3.metric("Delayed flights", f"{total_delayed:,}")
col4.metric("Delay rate", f"{delay_rate:.1%}")

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader("Flights by airline")
    chart_df = df.set_index("AIRLINE_NAME")[["TOTAL_FLIGHTS"]]
    st.bar_chart(chart_df)

with right:
    st.subheader("Flight status")
    st.write("Delayed flights:", f"{total_delayed:,}")
    st.write("Cancelled flights:", f"{total_cancelled:,}")

st.subheader("Airline details")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
