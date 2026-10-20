# Page skeleton: replace with real content
import streamlit as st

from db import LAST_3_DAYS, run_query

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #FFF1D6 0%,
            #FFD6B8 35%,
            #F4B6B8 70%,
            #D9B8D8 100%
        );
        color: #493447;
    }

    h1, h2, h3, p, label {
        color: #493447 !important;
    }

    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.65);
        padding: 18px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 4px 12px rgba(120, 75, 90, 0.08);
    }

    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Airport Performance")
st.caption("Flight activity · Latest three data days")

df = run_query(f"""
    SELECT
        a.AIRPORT_NAME,
        a.IATA_CODE,
        a.CITY,
        COUNT(*) AS TOTAL_FLIGHTS,
        SUM(CASE WHEN f.IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        SUM(CASE WHEN f.IS_CANCELLED THEN 1 ELSE 0 END) AS CANCELLED_FLIGHTS
    FROM FCT_FLIGHTS f
    JOIN DIM_AIRPORT a
        ON f.AIRPORT_KEY = a.AIRPORT_KEY
    WHERE {LAST_3_DAYS}
      AND f.IS_DELETED = FALSE
    GROUP BY
        a.AIRPORT_NAME,
        a.IATA_CODE,
        a.CITY
    ORDER BY TOTAL_FLIGHTS DESC
""")

total_flights = int(df["TOTAL_FLIGHTS"].sum())
total_delayed = int(df["DELAYED_FLIGHTS"].sum())
total_cancelled = int(df["CANCELLED_FLIGHTS"].sum())
airport_count = len(df)

delay_rate = total_delayed / total_flights if total_flights else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total flights", f"{total_flights:,}")
col2.metric("Airports", airport_count)
col3.metric("Delayed flights", f"{total_delayed:,}")
col4.metric("Delay rate", f"{delay_rate:.1%}")

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader("Flights by airport")
    chart_df = df.set_index("IATA_CODE")[["TOTAL_FLIGHTS"]]
    st.bar_chart(chart_df)

with right:
    st.subheader("Flight status")
    st.write("Delayed flights:", f"{total_delayed:,}")
    st.write("Cancelled flights:", f"{total_cancelled:,}")

st.subheader("Airport details")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
