
import html
 
import altair as alt
import streamlit as st
 
from db import LAST_3_DAYS, run_query
 
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
 
/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 16px;
    padding: 18px 20px;
    backdrop-filter: blur(10px);
}
[data-testid="stMetric"] * { color: #FFFFFF !important; }
 
hr { border-color: rgba(255, 255, 255, 0.25); }
 
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
    """Transparent HTML table with a small bar for the delayed share."""
    max_pct = float(data["DELAYED_PERCENT"].max()) or 1.0
    rows = ""
    for _, r in data.iterrows():
        width = 100 * float(r["DELAYED_PERCENT"]) / max_pct
        rows += (
            "<tr>"
            f"<td>{html.escape(str(r['AIRPORT_NAME']))}</td>"
            f"<td>{html.escape(str(r['IATA_CODE']))}</td>"
            f"<td>{html.escape(str(r['CITY']))}</td>"
            f"<td class='num'>{int(r['TOTAL_FLIGHTS'])}</td>"
            f"<td class='num'>{int(r['DELAYED_FLIGHTS'])}</td>"
            f"<td class='num'>{int(r['CANCELLED_FLIGHTS'])}</td>"
            f"<td><div class='cell'><div class='bar'><div class='fill' style='width:{width:.0f}%'></div></div>"
            f"<span>{float(r['DELAYED_PERCENT']):.1f}</span></div></td>"
            "</tr>"
        )
    return (
        "<div class='glass-wrap'><table class='glass'>"
        "<thead><tr><th>Airport</th><th>IATA</th><th>City</th>"
        "<th>Total flights</th><th>Delayed flights</th><th>Cancelled flights</th>"
        "<th>Delayed (%)</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )
 
 
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
    GROUP BY a.AIRPORT_NAME, a.IATA_CODE, a.CITY
""")
 
if df.empty:
    st.info("No flight data found for the latest three days.")
    st.stop()
 
# Snowflake returns decimals; convert so charts and tables can use them
for column in ["TOTAL_FLIGHTS", "DELAYED_FLIGHTS", "CANCELLED_FLIGHTS"]:
    df[column] = df[column].astype(int)
 
df["DELAYED_PERCENT"] = (100 * df["DELAYED_FLIGHTS"] / df["TOTAL_FLIGHTS"]).round(1)
df = df.sort_values("DELAYED_PERCENT", ascending=False).reset_index(drop=True)
 
total_flights = int(df["TOTAL_FLIGHTS"].sum())
total_delayed = int(df["DELAYED_FLIGHTS"].sum())
total_cancelled = int(df["CANCELLED_FLIGHTS"].sum())
delay_rate = total_delayed / total_flights if total_flights else 0
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total flights", f"{total_flights:,}")
col2.metric("Airports", len(df))
col3.metric("Cancelled flights", f"{total_cancelled:,}")
col4.metric("Delay rate", f"{delay_rate:.1%}")
 
st.divider()
 
st.subheader("Share of delayed flights per airport")
bars = (
    alt.Chart(df)
    .mark_bar(cornerRadiusEnd=6, color="#F3D6E0")
    .encode(
        x=alt.X(
            "DELAYED_PERCENT:Q",
            title="Delayed flights (%)",
            scale=alt.Scale(domain=[0, float(df["DELAYED_PERCENT"].max()) * 1.15 or 1]),
        ),
        y=alt.Y("AIRPORT_NAME:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        tooltip=[
            alt.Tooltip("AIRPORT_NAME:N", title="Airport"),
            alt.Tooltip("TOTAL_FLIGHTS:Q", title="Total flights"),
            alt.Tooltip("DELAYED_FLIGHTS:Q", title="Delayed flights"),
            alt.Tooltip("DELAYED_PERCENT:Q", title="Delayed (%)", format=".1f"),
        ],
    )
    .properties(height=28 * len(df) + 40)
)
labels = bars.mark_text(align="left", dx=5, color="#f6ecdc").encode(
    text=alt.Text("DELAYED_PERCENT:Q", format=".1f")
)
 
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
    "Delayed = more than 15 minutes late. "
    "Airports with few flights vary a lot in delay share."
)
