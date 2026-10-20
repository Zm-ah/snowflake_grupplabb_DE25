# Page skeleton: replace with real content
import streamlit as st

import altair as alt
import html

from db import LAST_3_DAYS, run_query


st.markdown("""
<style>
/* Sunset gradient background */
.stApp {
    background: linear-gradient(
        145deg,
        #16243D 0%,
        #3D405B 35%,
        #80566B 70%,
        #D98791 100%
    );
    color: #FFFFFF;
}

/* Header */
[data-testid="stHeader"] {
    background: transparent;
}

/* Main titles and text */
h1, h2, h3, p, label {
    color: #FFFFFF !important;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: #493447;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #FFF1D6 !important;
}

/* Selected page */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #80566B;
    border-radius: 10px;
}

/* Sidebar hover */
[data-testid="stSidebarNav"] a:hover {
    background-color: #705568;
    border-radius: 10px;
}

/* Airport statistic cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 16px;
    padding: 18px 20px;
    backdrop-filter: blur(10px);
}

[data-testid="stMetric"] * {
    color: #FFFFFF !important;
}

/* Captions */
[data-testid="stCaptionContainer"] * {
    color: #F3D6E0 !important;
}

/* Data table */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 12px;
}

/* Divider */
hr {
    border-color: rgba(255, 255, 255, 0.25);
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

col1, col2, col4 = st.columns(3)

col1.metric("Total flights", f"{total_flights:,}")
col2.metric("Airports", airport_count)
col4.metric("Delay rate", f"{delay_rate:.1%}")

st.divider()

left, right = st.columns([3, 2])

import altair as alt

with left:
    st.subheader("Flights by airport")

    chart_df = df[["AIRPORT_NAME", "TOTAL_FLIGHTS"]]

    chart = alt.Chart(chart_df).mark_bar().encode(
    y=alt.Y(
    "AIRPORT_NAME:N",
    title="Airport",
    sort=alt.EncodingSortField(
        field="TOTAL_FLIGHTS",
        order="descending"
    )
),
    x=alt.X(
        "TOTAL_FLIGHTS:Q",
        title="Number of flights"
    ),
    tooltip=["AIRPORT_NAME", "TOTAL_FLIGHTS"]
).properties(
    background="transparent"
).configure_view(
    strokeOpacity=0
)

chart = chart.configure_axis(
    grid=False,
    labelColor="white",
    titleColor="white"
)

st.altair_chart(
    chart,
    use_container_width=True,
    theme=None
)

with right:
    st.subheader("Flight status")
    st.write("Delayed flights:", f"{total_delayed:,}")
    st.write("Cancelled flights:", f"{total_cancelled:,}")


st.subheader("Airport details")
st.caption("Overview of flight activity by airport")


def glass_table(data) -> str:
    rows = ""

    for _, r in data.iterrows():
        total = int(r["TOTAL_FLIGHTS"])
        delayed = int(r["DELAYED_FLIGHTS"])
        cancelled = int(r["CANCELLED_FLIGHTS"])
        delayed_percent = delayed / total * 100 if total else 0

        rows += (
            "<tr>"
            f"<td>{html.escape(str(r['AIRPORT_NAME']))}</td>"
            f"<td>{html.escape(str(r['IATA_CODE']))}</td>"
            f"<td>{html.escape(str(r['CITY']))}</td>"
            f"<td class='num'>{total:,}</td>"
            f"<td class='num'>{delayed:,}</td>"
            f"<td><div class='cell'>"
            f"<div class='bar'><div class='fill' "
            f"style='width:{delayed_percent:.1f}%'></div></div>"
            f"<span>{delayed_percent:.1f}%</span>"
            f"</div></td>"
            f"<td class='num'>{cancelled:,}</td>"
            "</tr>"
        )

    return (
        "<div class='glass-wrap'><table class='glass'>"
        "<thead><tr>"
        "<th>Airport</th><th>IATA</th><th>City</th>"
        "<th>Total flights</th><th>Delayed flights</th>"
        "<th>Delayed (%)</th><th>Cancelled flights</th>"
        "</tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


st.markdown(glass_table(df), unsafe_allow_html=True)
