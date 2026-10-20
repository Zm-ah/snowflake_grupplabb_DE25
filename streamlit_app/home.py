
# Home page: hero section with video background and key numbers for the latest three days
import base64
from pathlib import Path

import streamlit as st

from db import LAST_3_DAYS, run_query

st.set_page_config(page_title="Flight Punctuality", layout="wide")

VIDEO_PATH = Path(__file__).parent / "static" / "landing.mp4"

CSS = """
<style>
/* Fallback background if no video exists */
.stApp { background: linear-gradient(160deg, #0b1220 0%, #16243d 60%, #1f3a5f 100%); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stHeader"] * { color: #ffffff !important; }

/* Video layer: darkened with a filter, so no overlay can cover the text */
#bg-video { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            object-fit: cover; z-index: 0; filter: brightness(0.45) saturate(1.1); }

/* Page content above the video */
.block-container, [data-testid="stMainBlockContainer"] { position: relative; z-index: 2; }
.hero-title, .hero-subtitle, [data-testid="stMetric"], [data-testid="stCaptionContainer"] {
    position: relative; z-index: 3; }

/* Hero text */
.hero-title { font-size: 4rem; font-weight: 800; color: #ffffff; margin-top: 8vh;
              text-shadow: 0 2px 24px rgba(0, 0, 0, 0.8); }
.hero-subtitle { font-size: 1.4rem; color: #ffffff; margin-bottom: 3rem;
                 text-shadow: 0 2px 12px rgba(0, 0, 0, 0.8); }

/* Metric cards: dark glass for strong contrast */
[data-testid="stMetric"] { background: rgba(8, 16, 36, 0.55);
                           border: 1px solid rgba(255, 255, 255, 0.25);
                           border-radius: 16px; padding: 18px 20px;
                           backdrop-filter: blur(12px); }
[data-testid="stMetric"] * { color: #ffffff !important; }

/* Caption text under the cards */
[data-testid="stCaptionContainer"] * { color: #e6eeff !important;
                                       text-shadow: 0 1px 8px rgba(0, 0, 0, 0.8); }
</style>
"""


@st.cache_resource
def load_video_base64(path: str) -> str:
    """Read the video file once and return it as a base64 string."""
    return base64.b64encode(Path(path).read_bytes()).decode()


def add_background(video_path: Path) -> None:
    """Add the page styling and, if the file exists, a looping video behind the page."""
    st.markdown(CSS, unsafe_allow_html=True)
    if video_path.exists():
        video_b64 = load_video_base64(str(video_path))
        st.markdown(
            f"""
            <video id="bg-video" autoplay muted loop playsinline>
                <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            </video>
            """,
            unsafe_allow_html=True,
        )

add_background(VIDEO_PATH)

st.markdown('<div class="hero-title">Flight Punctuality</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">How punctual are flights at Swedavia airports? '
    "A live view of the latest three days.</div>",
    unsafe_allow_html=True,
)

df = run_query(f"""
    SELECT
        COUNT(*) AS TOTAL_FLIGHTS,
        SUM(CASE WHEN IS_DELETED THEN 1 ELSE 0 END) AS DELETED_FLIGHTS,
        SUM(CASE WHEN HAS_ACTUAL_TIME THEN 1 ELSE 0 END) AS OPERATED_FLIGHTS,
        SUM(CASE WHEN IS_DELAYED THEN 1 ELSE 0 END) AS DELAYED_FLIGHTS,
        SUM(CASE WHEN IS_CANCELLED THEN 1 ELSE 0 END) AS CANCELLED_FLIGHTS,
        MIN(FLIGHT_DATE) AS FIRST_DATE,
        MAX(FLIGHT_DATE) AS LAST_DATE
    FROM FCT_FLIGHTS
    WHERE {LAST_3_DAYS}
""")

total = int(df["TOTAL_FLIGHTS"][0])
deleted = int(df["DELETED_FLIGHTS"][0])
operated = int(df["OPERATED_FLIGHTS"][0])
delayed = int(df["DELAYED_FLIGHTS"][0])
cancelled = int(df["CANCELLED_FLIGHTS"][0])
scheduled = total - deleted  # flights that were actually in the schedule
first_date = df["FIRST_DATE"][0]
last_date = df["LAST_DATE"][0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Scheduled flights", scheduled)
col2.metric("Operated flights", operated)
col3.metric("Delayed (of operated)", f"{delayed} ({delayed / operated:.1%})")
col4.metric("Cancelled (of scheduled)", f"{cancelled} ({cancelled / scheduled:.1%})")

st.caption(
    f"Data from Swedavia airports, {first_date} to {last_date} (latest three days). "
    "Delayed = more than 15 minutes after scheduled time. "
    "Deleted entries (removed from the schedule) are excluded."
)