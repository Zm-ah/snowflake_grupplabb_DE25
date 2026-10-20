# Airlines page: punctuality per airline for the latest three days
import altair as alt
import streamlit as st

from db import LAST_3_DAYS, run_query

st.title("Airlines")

min_flights = st.slider("Minimum number of operated flights per airline", 5, 100, 20)

df = run_query(f"""
    SELECT
        COALESCE(a.AIRLINE_NAME, f.AIRLINE_KEY) AS AIRLINE,
        COUNT(*) AS OPERATED_FLIGHTS,
        SUM(CASE WHEN f.IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        ROUND(100 * SUM(CASE WHEN f.IS_DELAYED THEN 1 ELSE 0 END) / COUNT(*), 1) AS DELAYED_PERCENT,
        ROUND(AVG(f.DELAY_MINUTES), 1) AS AVG_DELAY_MINUTES
    FROM FCT_FLIGHTS AS f
    LEFT JOIN DIM_AIRLINE AS a
        ON f.AIRLINE_KEY = a.AIRLINE_KEY
    WHERE f.HAS_ACTUAL_TIME
      AND {LAST_3_DAYS}
    GROUP BY AIRLINE
    HAVING COUNT(*) >= {min_flights}
    ORDER BY DELAYED_PERCENT DESC
""")

if df.empty:
    st.info("No airlines match the selected minimum. Try a lower value.")
    st.stop()

# Snowflake returns decimals; convert to float so the chart can use them
for column in ["DELAYED_PERCENT", "AVG_DELAY_MINUTES"]:
    df[column] = df[column].astype(float)

chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("DELAYED_PERCENT:Q", title="Delayed flights (%)"),
        y=alt.Y("AIRLINE:N", sort="-x", title=None),
        tooltip=["AIRLINE", "OPERATED_FLIGHTS", "DELAYED_FLIGHTS", "DELAYED_PERCENT"],
    )
)
st.altair_chart(chart, use_container_width=True)

st.dataframe(df, hide_index=True)
st.caption("Only flights that have operated are counted. Delayed = more than 15 minutes late.")