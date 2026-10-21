# Time trends page: when do delays happen? Latest three days, per day and per hour

import altair as alt
import streamlit as st

from db import LAST_3_DAYS, run_query

# --- Settings ---
# Hide hours with fewer operated flights than this (too small a sample)
MIN_FLIGHTS_PER_HOUR = 10
# A day counts as partial if fewer than this share of its expected flights
# have an actual time yet
PARTIAL_THRESHOLD = 0.9

# --- Palette: change here if the group updates the colors ---
COLOR_ARRIVALS = "#FFF1D6"
COLOR_DEPARTURES = "#D98791"
TEXT_COLOR = "#f6ecdc"
DIRECTION_SCALE = alt.Scale(
    domain=["arrivals", "departures"], range=[COLOR_ARRIVALS, COLOR_DEPARTURES]
)

st.title("Time trends")

# Same sunset theme as the Airlines and Airports pages
st.markdown(
    """
    <style>
    /* Sunset gradient background */
    .stApp {
        background: linear-gradient(145deg, #16243D 0%, #3D405B 35%, #80566B 70%, #D98791 100%);
        color: #FFFFFF;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stHeader"] * { color: #FFFFFF !important; }

    /* Titles and text */
    h1, h2, h3, p, label { color: #FFFFFF !important; }
    [data-testid="stCaptionContainer"] * { color: #F3D6E0 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #493447; }
    [data-testid="stSidebar"] * { color: #FFF1D6 !important; }
    [data-testid="stSidebarNav"] a[aria-current="page"] { background-color: #80566B; border-radius: 10px; }
    [data-testid="stSidebarNav"] a:hover { background-color: #705568; border-radius: 10px; }

    </style>
    """,
    unsafe_allow_html=True,
)

def style_chart(chart):
    """Transparent background and light text so charts fit the dark page."""
    return (
        chart.properties(background="transparent")
        .configure_axis(
            labelColor=TEXT_COLOR,
            titleColor=TEXT_COLOR,
            gridColor="rgba(255, 255, 255, 0.12)",
            domainColor="rgba(255, 255, 255, 0.35)",
            tickColor="rgba(255, 255, 255, 0.35)",
        )
        .configure_legend(labelColor=TEXT_COLOR, titleColor=TEXT_COLOR)
        .configure_view(stroke=None)
    )


# ---------- Per day ----------
# EXPECTED_FLIGHTS = flights that should have an actual time (not deleted, not
# cancelled). It is used to detect a day that is still incomplete.
daily = run_query(f"""
    SELECT
        FLIGHT_DATE,
        DIRECTION,
        COUNT_IF(HAS_ACTUAL_TIME) AS OPERATED_FLIGHTS,
        COUNT_IF(NOT IS_DELETED AND NOT IS_CANCELLED) AS EXPECTED_FLIGHTS,
        COUNT_IF(IS_DELAYED) AS DELAYED_FLIGHTS,
        ROUND(100 * COUNT_IF(IS_DELAYED) / NULLIF(COUNT_IF(HAS_ACTUAL_TIME), 0), 1) AS DELAYED_PERCENT,
        ROUND(MEDIAN(DELAY_MINUTES), 1) AS MEDIAN_DELAY_MINUTES
    FROM FCT_FLIGHTS
    WHERE {LAST_3_DAYS}
    GROUP BY FLIGHT_DATE, DIRECTION
    ORDER BY FLIGHT_DATE, DIRECTION
""")

daily = daily[daily["OPERATED_FLIGHTS"] > 0]
if daily.empty:
    st.info("No operated flights found for the latest three days.")
    st.stop()

# Snowflake returns decimals; convert so charts and tables can use them
for column in ["DELAYED_PERCENT", "MEDIAN_DELAY_MINUTES"]:
    daily[column] = daily[column].astype(float)
for column in ["OPERATED_FLIGHTS", "EXPECTED_FLIGHTS", "DELAYED_FLIGHTS"]:
    daily[column] = daily[column].astype(int)
daily["FLIGHT_DATE"] = daily["FLIGHT_DATE"].astype(str)

# Find days where too few flights have an actual time yet
per_day = daily.groupby("FLIGHT_DATE")[["OPERATED_FLIGHTS", "EXPECTED_FLIGHTS"]].sum()
completeness = per_day["OPERATED_FLIGHTS"] / per_day["EXPECTED_FLIGHTS"].where(
    per_day["EXPECTED_FLIGHTS"] > 0
)
partial_days = list(completeness[completeness < PARTIAL_THRESHOLD].index)

# Label shown on the x-axis: partial days are marked clearly
daily["DAY"] = daily["FLIGHT_DATE"].apply(
    lambda d: f"{d} (partial)" if d in partial_days else d
)
day_order = daily.sort_values("FLIGHT_DATE")["DAY"].drop_duplicates().tolist()

st.subheader("Share of delayed flights per day")
daily_line = (
    alt.Chart(daily)
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X(
            "DAY:O",
            title="Date",
            sort=day_order,
            axis=alt.Axis(labelAngle=0, labelLimit=200),
        ),
        y=alt.Y(
            "DELAYED_PERCENT:Q",
            title="Delayed flights (%)",
            scale=alt.Scale(zero=True),
        ),
        color=alt.Color("DIRECTION:N", scale=DIRECTION_SCALE, title="Direction"),
        tooltip=[
            alt.Tooltip("DAY:O", title="Date"),
            alt.Tooltip("DIRECTION:N", title="Direction"),
            alt.Tooltip("OPERATED_FLIGHTS:Q", title="Operated flights"),
            alt.Tooltip("DELAYED_PERCENT:Q", title="Delayed (%)", format=".1f"),
        ],
    )
    .properties(height=320)
)
st.altair_chart(style_chart(daily_line), use_container_width=True, theme=None)

for day in partial_days:
    st.caption(
        f"{day} is incomplete: only {int(per_day.loc[day, 'OPERATED_FLIGHTS'])} of about "
        f"{int(per_day.loc[day, 'EXPECTED_FLIGHTS'])} expected flights have an actual time yet, "
        "so its delay share rests on a small sample and is not a trend."
    )

# ---------- Per hour ----------
hourly = run_query(f"""
    SELECT
        HOUR(CONVERT_TIMEZONE('UTC', 'Europe/Stockholm', SCHEDULED_UTC::TIMESTAMP_NTZ)) AS HOUR_OF_DAY,
        DIRECTION,
        COUNT(*) AS OPERATED_FLIGHTS,
        ROUND(100 * SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) / COUNT(*), 1) AS DELAYED_PERCENT
    FROM FCT_FLIGHTS
    WHERE HAS_ACTUAL_TIME
      AND {LAST_3_DAYS}
    GROUP BY HOUR_OF_DAY, DIRECTION
    HAVING COUNT(*) >= {MIN_FLIGHTS_PER_HOUR}
    ORDER BY HOUR_OF_DAY, DIRECTION
""")

st.subheader("Share of delayed flights by hour of day")
if hourly.empty:
    st.info("Not enough flights per hour to show this chart.")
else:
    hourly["DELAYED_PERCENT"] = hourly["DELAYED_PERCENT"].astype(float)
    hourly["OPERATED_FLIGHTS"] = hourly["OPERATED_FLIGHTS"].astype(int)
    hourly["HOUR_OF_DAY"] = hourly["HOUR_OF_DAY"].astype(int)

    hourly_line = (
        alt.Chart(hourly)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X(
                "HOUR_OF_DAY:O",
                title="Scheduled hour (Swedish time)",
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(
                "DELAYED_PERCENT:Q",
                title="Delayed flights (%)",
                scale=alt.Scale(zero=True),
            ),
            color=alt.Color("DIRECTION:N", scale=DIRECTION_SCALE, title="Direction"),
            tooltip=[
                alt.Tooltip("HOUR_OF_DAY:O", title="Hour"),
                alt.Tooltip("DIRECTION:N", title="Direction"),
                alt.Tooltip("OPERATED_FLIGHTS:Q", title="Operated flights"),
                alt.Tooltip("DELAYED_PERCENT:Q", title="Delayed (%)", format=".1f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(style_chart(hourly_line), use_container_width=True, theme=None)

st.caption(
    "Latest three days in the data. Only flights that have operated are counted. "
    "Delayed = more than 15 minutes late. Days without a pipeline run are missing. "
    "Hours with very few flights are hidden, since small samples give misleading "
    "percentages. Hours are in Swedish local time."
)