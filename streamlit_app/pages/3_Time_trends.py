# Time trends page: when do delays happen? Latest three days, per day and per hour
import altair as alt
import streamlit as st

from db import LAST_3_DAYS, run_query

# Settings 
MIN_FLIGHTS_PER_HOUR = 10  # hide hours with too small a sample
PARTIAL_THRESHOLD = 0.9    # a day is partial if less than this share 
                        # of expected flights has an actual time

# Palette: change here if the group updates the colors
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


def delay_line_chart(data, x, x_title, x_sort=alt.Undefined):
    """Line chart of the delayed share, one line per direction, styled for the dark page."""
    chart = (
        alt.Chart(data)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X(f"{x}:O", title=x_title, sort=x_sort,
                    axis=alt.Axis(labelAngle=0, labelLimit=200)),
            y=alt.Y("DELAYED_PERCENT:Q", title="Delayed flights (%)",
                    scale=alt.Scale(zero=True)),
            color=alt.Color("DIRECTION:N", scale=DIRECTION_SCALE, title="Direction"),
            tooltip=[
                alt.Tooltip(f"{x}:O", title=x_title),
                alt.Tooltip("DIRECTION:N", title="Direction"),
                alt.Tooltip("OPERATED_FLIGHTS:Q", title="Operated flights"),
                alt.Tooltip("DELAYED_PERCENT:Q", title="Delayed (%)", format=".1f"),
            ],
        )
        .properties(height=320, background="transparent")
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
    st.altair_chart(chart, use_container_width=True, theme=None)


# Per day
# EXPECTED_FLIGHTS = flights that should have an actual time (not deleted or cancelled). 
daily = run_query(f"""
    SELECT
        FLIGHT_DATE,
        DIRECTION,
        COUNT_IF(HAS_ACTUAL_TIME) AS OPERATED_FLIGHTS,
        COUNT_IF(NOT IS_DELETED AND NOT IS_CANCELLED) AS EXPECTED_FLIGHTS,
        ROUND(100 * COUNT_IF(IS_DELAYED) / NULLIF(COUNT_IF(HAS_ACTUAL_TIME), 0), 1) AS DELAYED_PERCENT
    FROM FCT_FLIGHTS
    WHERE {LAST_3_DAYS}
    GROUP BY FLIGHT_DATE, DIRECTION
    ORDER BY FLIGHT_DATE, DIRECTION
""")

# Snowflake returns decimals and dates, convert so charts can use them
daily = daily[daily["OPERATED_FLIGHTS"] > 0].astype(
    {"DELAYED_PERCENT": float, "OPERATED_FLIGHTS": int,
     "EXPECTED_FLIGHTS": int, "FLIGHT_DATE": str}
)
if daily.empty:
    st.info("No operated flights found for the latest three days.")
    st.stop()

# Days where too few flights have an actual time yet are marked as partial
per_day = daily.groupby("FLIGHT_DATE")[["OPERATED_FLIGHTS", "EXPECTED_FLIGHTS"]].sum()
share = per_day["OPERATED_FLIGHTS"] / per_day["EXPECTED_FLIGHTS"].where(
    per_day["EXPECTED_FLIGHTS"] > 0
)
partial_days = list(share[share < PARTIAL_THRESHOLD].index)
daily["DAY"] = daily["FLIGHT_DATE"] + daily["FLIGHT_DATE"].isin(partial_days).map(
    {True: " (partial)", False: ""}
)

st.subheader("Share of delayed flights per day")
delay_line_chart(daily, "DAY", "Date", x_sort=sorted(daily["DAY"].unique()))

for day in partial_days:
    p = per_day.loc[day]
    st.caption(
        f"{day} is incomplete: only {int(p['OPERATED_FLIGHTS'])} of about "
        f"{int(p['EXPECTED_FLIGHTS'])} expected flights have an actual time yet, "
        "so its delay share rests on a small sample and is not a trend."
    )

# Per hour
hourly = run_query(f"""
    SELECT
        HOUR(CONVERT_TIMEZONE('UTC', 'Europe/Stockholm', SCHEDULED_UTC::TIMESTAMP_NTZ)) AS HOUR_OF_DAY,
        DIRECTION,
        COUNT(*) AS OPERATED_FLIGHTS,
        ROUND(100 * COUNT_IF(IS_DELAYED) / COUNT(*), 1) AS DELAYED_PERCENT
    FROM FCT_FLIGHTS
    WHERE HAS_ACTUAL_TIME AND {LAST_3_DAYS}
    GROUP BY HOUR_OF_DAY, DIRECTION
    HAVING COUNT(*) >= {MIN_FLIGHTS_PER_HOUR}
    ORDER BY HOUR_OF_DAY, DIRECTION
""").astype({"DELAYED_PERCENT": float, "OPERATED_FLIGHTS": int, "HOUR_OF_DAY": int})

st.subheader("Share of delayed flights by hour of day")
if hourly.empty:
    st.info("Not enough flights per hour to show this chart.")
else:
    delay_line_chart(hourly, "HOUR_OF_DAY", "Scheduled hour (Swedish time)")

st.caption(
    "Latest three days in the data. Only flights that have operated are counted. "
    "Flights are 'delayed' when they are more than 15 minutes late. Hours are in Swedish local time. "
    "Hours with very few flights are hidden, since small samples give misleading "
    "percentages. "
)