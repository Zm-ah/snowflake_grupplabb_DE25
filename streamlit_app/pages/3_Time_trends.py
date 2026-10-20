# Time trends page: when do delays happen? Daily and hour-of-day view
import html

import altair as alt
import streamlit as st

from db import LAST_3_DAYS, run_query

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

    /* Transparent glass table */
    .glass-wrap { border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 12px;
                  overflow: hidden; background: rgba(255, 255, 255, 0.12);
                  backdrop-filter: blur(10px); }
    table.glass { width: 100%; border-collapse: collapse; color: #FFFFFF; }
    table.glass th { text-align: left; padding: 12px 14px; background: rgba(255, 255, 255, 0.10);
                     font-weight: 600; color: #FFF1D6; }
    table.glass td { padding: 10px 14px; border-top: 1px solid rgba(255, 255, 255, 0.25); }
    table.glass tr:hover td { background: rgba(255, 255, 255, 0.08); }
    table.glass td.num { text-align: right; }
    .cell { display: flex; align-items: center; gap: 10px; }
    .bar { flex: 1; min-width: 120px; height: 10px; border-radius: 5px;
           background: rgba(255, 255, 255, 0.18); overflow: hidden; }
    .fill { height: 100%; background: #F3D6E0; border-radius: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def glass_table(data) -> str:
    """Build a transparent HTML table with a small bar for the delayed share."""
    max_pct = float(data["DELAYED_PERCENT"].max()) or 1.0
    rows = ""
    for _, r in data.iterrows():
        width = 100 * float(r["DELAYED_PERCENT"]) / max_pct
        rows += (
            "<tr>"
            f"<td>{html.escape(str(r['FLIGHT_DATE']))}</td>"
            f"<td>{html.escape(str(r['DIRECTION']))}</td>"
            f"<td class='num'>{int(r['OPERATED_FLIGHTS'])}</td>"
            f"<td class='num'>{int(r['DELAYED_FLIGHTS'])}</td>"
            f"<td><div class='cell'><div class='bar'><div class='fill' style='width:{width:.0f}%'></div></div>"
            f"<span>{float(r['DELAYED_PERCENT']):.1f}</span></div></td>"
            f"<td class='num'>{float(r['MEDIAN_DELAY_MINUTES']):.1f}</td>"
            "</tr>"
        )
    return (
        "<div class='glass-wrap'><table class='glass'>"
        "<thead><tr><th>Date</th><th>Direction</th><th>Operated flights</th>"
        "<th>Delayed flights</th><th>Delayed (%)</th><th>Median delay (min)</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
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


period = st.radio(
    "Period", ["All loaded days", "Latest three days"], horizontal=True
)
period_filter = LAST_3_DAYS if period == "Latest three days" else "1 = 1"

min_flights = st.slider(
    "Minimum number of operated flights per hour and direction", 5, 100, 20
)

# ---------- Per day ----------
daily = run_query(f"""
    SELECT
        FLIGHT_DATE,
        DIRECTION,
        COUNT(*) AS OPERATED_FLIGHTS,
        SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        ROUND(100 * SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) / COUNT(*), 1) AS DELAYED_PERCENT,
        ROUND(MEDIAN(DELAY_MINUTES), 1) AS MEDIAN_DELAY_MINUTES
    FROM FCT_FLIGHTS
    WHERE HAS_ACTUAL_TIME
      AND {period_filter}
    GROUP BY FLIGHT_DATE, DIRECTION
    ORDER BY FLIGHT_DATE, DIRECTION
""")

if daily.empty:
    st.info("No operated flights found for the selected period.")
    st.stop()

# Snowflake returns decimals; convert so charts and tables can use them.
# Dates become text so the axis only shows days that exist in the data.
for column in ["DELAYED_PERCENT", "MEDIAN_DELAY_MINUTES"]:
    daily[column] = daily[column].astype(float)
for column in ["OPERATED_FLIGHTS", "DELAYED_FLIGHTS"]:
    daily[column] = daily[column].astype(int)
daily["FLIGHT_DATE"] = daily["FLIGHT_DATE"].astype(str)

st.subheader("Share of delayed flights per day")
daily_line = (
    alt.Chart(daily)
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X("FLIGHT_DATE:O", title="Date", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(
            "DELAYED_PERCENT:Q",
            title="Delayed flights (%)",
            scale=alt.Scale(zero=True),
        ),
        color=alt.Color("DIRECTION:N", scale=DIRECTION_SCALE, title="Direction"),
        tooltip=[
            alt.Tooltip("FLIGHT_DATE:O", title="Date"),
            alt.Tooltip("DIRECTION:N", title="Direction"),
            alt.Tooltip("OPERATED_FLIGHTS:Q", title="Operated flights"),
            alt.Tooltip("DELAYED_PERCENT:Q", title="Delayed (%)", format=".1f"),
        ],
    )
    .properties(height=320)
)
st.altair_chart(style_chart(daily_line), use_container_width=True, theme=None)

st.subheader("Operated flights per day")
daily_volume = (
    alt.Chart(daily)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X("FLIGHT_DATE:O", title="Date", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("OPERATED_FLIGHTS:Q", title="Operated flights"),
        color=alt.Color("DIRECTION:N", scale=DIRECTION_SCALE, title="Direction"),
        tooltip=[
            alt.Tooltip("FLIGHT_DATE:O", title="Date"),
            alt.Tooltip("DIRECTION:N", title="Direction"),
            alt.Tooltip("OPERATED_FLIGHTS:Q", title="Operated flights"),
        ],
    )
    .properties(height=280)
)
st.altair_chart(style_chart(daily_volume), use_container_width=True, theme=None)

# ---------- Per hour ----------
hourly = run_query(f"""
    SELECT
        HOUR(CONVERT_TIMEZONE('UTC', 'Europe/Stockholm', SCHEDULED_UTC::TIMESTAMP_NTZ)) AS HOUR_OF_DAY,
        DIRECTION,
        COUNT(*) AS OPERATED_FLIGHTS,
        ROUND(100 * SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) / COUNT(*), 1) AS DELAYED_PERCENT
    FROM FCT_FLIGHTS
    WHERE HAS_ACTUAL_TIME
      AND {period_filter}
    GROUP BY HOUR_OF_DAY, DIRECTION
    HAVING COUNT(*) >= {min_flights}
    ORDER BY HOUR_OF_DAY, DIRECTION
""")

st.subheader("Share of delayed flights by hour of day")
if hourly.empty:
    st.info("No hours match the selected minimum. Try a lower value.")
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

# ---------- Details ----------
st.subheader("Details per day")
st.markdown(
    glass_table(daily.sort_values(["FLIGHT_DATE", "DIRECTION"], ascending=[False, True])),
    unsafe_allow_html=True,
)

st.caption(
    "Only flights that have operated are counted. Delayed = more than 15 minutes late. "
    "Days without a pipeline run are missing from the charts, and the most recent day "
    "may be incomplete because later flights have no actual time yet. "
    "Hours with fewer flights than the slider minimum are hidden, since small samples "
    "give misleading percentages. Hours are in Swedish local time."
)