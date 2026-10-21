# Airlines page: punctuality per airline for the latest three days
import html

import altair as alt
import streamlit as st

from db import LAST_3_DAYS, run_query

st.title("Airlines")

# Same sunset theme as the Airports page
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
            f"<td>{html.escape(str(r['AIRLINE']))}</td>"
            f"<td class='num'>{int(r['OPERATED_FLIGHTS'])}</td>"
            f"<td class='num'>{int(r['DELAYED_FLIGHTS'])}</td>"
            f"<td><div class='cell'><div class='bar'><div class='fill' style='width:{width:.0f}%'></div></div>"
            f"<span>{float(r['DELAYED_PERCENT']):.1f}</span></div></td>"
            f"<td class='num'>{float(r['MEDIAN_DELAY_MINUTES']):.1f}</td>"
            "</tr>"
        )
    return (
        "<div class='glass-wrap'><table class='glass'>"
        "<thead><tr><th>Airline</th><th>Operated flights</th><th>Delayed flights</th>"
        "<th>Delayed (%)</th><th>Median delay (min)</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


min_flights = st.slider("Minimum number of operated flights per airline", 5, 100, 20)

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
    GROUP BY AIRLINE
    HAVING COUNT(*) >= {min_flights}
    ORDER BY DELAYED_PERCENT DESC
""")

if df.empty:
    st.info("No airlines match the selected minimum. Try a lower value.")
    st.stop()

# Snowflake returns decimals; convert to float so charts and tables can use them
for column in ["DELAYED_PERCENT", "MEDIAN_DELAY_MINUTES"]:
    df[column] = df[column].astype(float)

st.subheader("Share of delayed flights per airline")
bars = (
    alt.Chart(df)
   .mark_bar(cornerRadiusEnd=6, color="#F3D6E0")
    .encode(
        x=alt.X(
            "DELAYED_PERCENT:Q",
            title="Delayed flights (%)",
            scale=alt.Scale(domain=[0, float(df["DELAYED_PERCENT"].max()) * 1.15]),
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
labels = bars.mark_text(align="left", dx=5, color="#f6ecdc").encode(
    text=alt.Text("DELAYED_PERCENT:Q", format=".1f")
)

# Transparent chart background and light axis text for the dark page
chart = (
    (bars + labels)
    .properties(background="transparent")
    .configure_axis(
        labelColor="#f6ecdc",
        titleColor="#f6ecdc",
        gridColor="rgba(255, 255, 255, 0.12)",
        domainColor="rgba(255, 255, 255, 0.35)",
        tickColor="rgba(255, 255, 255, 0.35)",
    )
    .configure_view(stroke=None)
)
st.altair_chart(chart, use_container_width=True, theme=None)

st.subheader("Details")
st.markdown(glass_table(df), unsafe_allow_html=True)

st.caption(
    "Only flights that have operated are counted. Delayed = more than 15 minutes late. "
    "Median delay is used because a few extreme delays would distort the average. "
    "Airlines with few flights vary a lot, so use the slider to set a minimum."
)