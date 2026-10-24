# Airlines page: punctuality per airline for the latest three days
import altair as alt
import streamlit as st

from db import LAST_3_DAYS, run_query
from styles import BAR_COLOR, LABEL_COLOR, apply_styles, glass_table, style_chart

apply_styles()

st.title("Airlines")

# Filters
min_flights = st.slider("Minimum number of operated flights per airline", 5, 100, 20)

# Direction filter: the options come straight from the data
directions = run_query("SELECT DISTINCT DIRECTION FROM FCT_FLIGHTS ORDER BY 1")["DIRECTION"].dropna().tolist()
direction = st.selectbox("Direction", ["All"] + directions)
direction_filter = "" if direction == "All" else f"AND f.DIRECTION = '{direction}'"

df = run_query(f"""
    SELECT
        COALESCE(a.AIRLINE_NAME, f.AIRLINE_KEY) AS AIRLINE,
        COUNT(*) AS OPERATED_FLIGHTS,
        SUM(CASE WHEN f.IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        ROUND(100 * SUM(CASE WHEN f.IS_DELAYED THEN 1 ELSE 0 END) / COUNT(*), 1) AS DELAYED_PERCENT,
        ROUND(MEDIAN(f.DELAY_MINUTES), 1) AS MEDIAN_DELAY_MINUTES
    FROM FCT_FLIGHTS AS f
    LEFT JOIN DIM_AIRLINE AS a
        ON f.AIRLINE_KEY = a.AIRLINE_KEY
    WHERE f.HAS_ACTUAL_TIME
      AND {LAST_3_DAYS}
      {direction_filter}
    GROUP BY AIRLINE
    HAVING COUNT(*) >= {min_flights}
    ORDER BY DELAYED_PERCENT DESC
""")

if df.empty:
    st.info("No airlines match the selected filters. Try a lower minimum.")
    st.stop()

# Snowflake returns decimals; convert to float so charts and tables can use them
for column in ["DELAYED_PERCENT", "MEDIAN_DELAY_MINUTES"]:
    df[column] = df[column].astype(float)

# Chart: share of delayed flights per airline
bars = (
    alt.Chart(df)
    .mark_bar(cornerRadiusEnd=6, color=BAR_COLOR)
    .encode(
        x=alt.X(
            "DELAYED_PERCENT:Q",
            title="Delayed flights (%)",
            scale=alt.Scale(domain=[0, float(df["DELAYED_PERCENT"].max()) * 1.15 or 1]),
        ),
        y=alt.Y("AIRLINE:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        tooltip=[
            alt.Tooltip("AIRLINE:N", title="Airline"),
            alt.Tooltip("OPERATED_FLIGHTS:Q", title="Operated flights"),
            alt.Tooltip("DELAYED_FLIGHTS:Q", title="Delayed flights"),
            alt.Tooltip("DELAYED_PERCENT:Q", title="Delayed (%)", format=".1f"),
        ],
    )
    .properties(height=28 * len(df) + 40)
)
labels = bars.mark_text(align="left", dx=5, color=LABEL_COLOR).encode(
    text=alt.Text("DELAYED_PERCENT:Q", format=".1f")
)

st.subheader("Share of delayed flights per airline")
st.altair_chart(style_chart(bars + labels), use_container_width=True, theme=None)

# Table with the same numbers
st.subheader("Details")
glass_table(
    df,
    columns=[
        ("AIRLINE", "Airline", "text"),
        ("OPERATED_FLIGHTS", "Operated flights", "int"),
        ("DELAYED_FLIGHTS", "Delayed flights", "int"),
        ("DELAYED_PERCENT", "Delayed (%)", "float"),
        ("MEDIAN_DELAY_MINUTES", "Median delay (min)", "float"),
    ],
    bar_column="DELAYED_PERCENT",
)

st.caption(
    "Only flights that have operated are counted. Delayed = more than 15 minutes late. "
    "Median delay is used because a few extreme delays would distort the average. "
    "Airlines with few flights vary a lot, so use the slider to set a minimum."
)