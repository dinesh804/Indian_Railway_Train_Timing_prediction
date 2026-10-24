# ============================================================
# DYNAMIC TRAIN ETA INTELLIGENCE DASHBOARD
# ============================================================

import sys
from pathlib import Path
from datetime import datetime

# ============================================================
# PATH
# ============================================================

DASHBOARD_DIR = Path(__file__).resolve().parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from websocket_client import get_train_update

from charts import (
    create_eta_gauge,
    create_progress_chart,
    create_history_chart,
    create_delay_chart
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dynamic Train ETA Intelligence",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM HTML FUNCTION
# ============================================================

def render_html(html_content):
    """
    Render HTML using Streamlit's native HTML renderer.
    This avoids HTML being displayed as plain text/code.
    """

    st.html(html_content)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       MAIN APPLICATION
       ====================================================== */

    .stApp {
        background: #0e1117;
    }

    .main {
        background: #0e1117;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background: #11151d;
        border-right: 1px solid #29313d;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }


    /* ======================================================
       HEADER
       ====================================================== */

    .dashboard-title {
        color: #f8fafc;
        font-size: 34px;
        font-weight: 750;
        line-height: 1.2;
        margin-bottom: 8px;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 15px;
    }


    /* ======================================================
       LIVE BADGE
       ====================================================== */

    .live-indicator {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;

        padding: 9px 16px;

        background: #062e24;

        color: #34d399;

        border: 1px solid #065f46;

        border-radius: 25px;

        font-size: 13px;

        font-weight: 700;
    }

    .live-dot {
        width: 9px;
        height: 9px;

        background: #10b981;

        border-radius: 50%;
    }


    /* ======================================================
       TRAIN INFO
       ====================================================== */

    .info-box {
        background: #171b24;

        border: 1px solid #2b3240;

        border-radius: 14px;

        padding: 18px 22px;

        margin-bottom: 16px;

        color: #f8fafc;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.15);
    }

    .train-name {
        font-size: 19px;
        font-weight: 700;
        color: #f8fafc;
    }

    .info-label {
        color: #94a3b8;
        font-size: 12px;
    }

    .info-value {
        color: #f8fafc;
        font-weight: 600;
    }

    .separator {
        color: #475569;
        margin: 0 12px;
    }


    /* ======================================================
       KPI CARDS
       ====================================================== */

    .kpi-card {
        background: #171b24;

        border: 1px solid #2b3240;

        border-radius: 14px;

        padding: 19px;

        min-height: 130px;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.15);
    }

    .kpi-title {
        color: #94a3b8;

        font-size: 12px;

        font-weight: 700;

        margin-bottom: 10px;

        letter-spacing: 0.4px;
    }

    .kpi-value {
        color: #f8fafc;

        font-size: 27px;

        font-weight: 750;

        line-height: 1.2;
    }

    .kpi-subtitle {
        color: #64748b;

        font-size: 12px;

        margin-top: 8px;
    }


    /* ======================================================
       SECTION TITLES
       ====================================================== */

    .section-title {
        color: #f8fafc;

        font-size: 20px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 12px;
    }


    /* ======================================================
       STREAMLIT METRICS
       ====================================================== */

    [data-testid="stMetric"] {
        background: #171b24;

        border: 1px solid #2b3240;

        border-radius: 12px;

        padding: 15px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }


    /* ======================================================
       EXPANDERS
       ====================================================== */

    [data-testid="stExpander"] {
        background: #171b24;

        border: 1px solid #2b3240;

        border-radius: 12px;
    }


    /* ======================================================
       DATAFRAME
       ====================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* ======================================================
       DIVIDER
       ====================================================== */

    hr {
        border-color: #29313d !important;
    }


    /* ======================================================
       INPUT
       ====================================================== */

    .stTextInput input {
        background: #171b24 !important;

        color: #f8fafc !important;

        border: 1px solid #334155 !important;

        border-radius: 8px !important;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "last_update" not in st.session_state:
    st.session_state.last_update = None

if "connection_error" not in st.session_state:
    st.session_state.connection_error = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚆 Train Control")

    st.markdown("---")

    train_number = st.text_input(
        "Train Number",
        value="12653",
        help="Enter the railway train number."
    )

    train_number = train_number.strip()

    refresh_seconds = st.slider(
        "Dashboard Refresh",
        min_value=30,
        max_value=300,
        value=60,
        step=30
    )

    st.markdown("---")

    st.markdown("### System Architecture")

    st.markdown(
        """
        **LIVE DATA PIPELINE**

        🛰️ RailRadar API

        ↓

        🔄 Data Normalization

        ↓

        🧠 ML ETA Engine

        ↓

        ⚡ FastAPI

        ↓

        🔌 WebSocket

        ↓

        📊 Streamlit
        """
    )

    st.markdown("---")

    st.markdown("### System Status")

    st.success("Dashboard Active")

    st.caption(
        "Dynamic Train ETA Forecasting System"
    )


# ============================================================
# AUTO REFRESH
# ============================================================

st_autorefresh(
    interval=refresh_seconds * 1000,
    key="train_eta_refresh"
)


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [5, 1]
)


with header_left:

    render_html(
        """
        <div class="dashboard-title">
            🚆 Dynamic Train ETA Intelligence
        </div>

        <div class="dashboard-subtitle">
            Real-time railway monitoring and
            machine-learning ETA forecasting
        </div>
        """
    )


with header_right:

    render_html(
        """
        <div class="live-indicator">
            <span class="live-dot"></span>
            LIVE
        </div>
        """
    )


st.markdown("---")


# ============================================================
# VALIDATE TRAIN NUMBER
# ============================================================

if not train_number:

    st.warning("Please enter a train number.")

    st.stop()


# ============================================================
# GET LIVE DATA
# ============================================================

with st.spinner(
    f"Fetching live data for train {train_number}..."
):

    try:

        train_data = get_train_update(
            train_number
        )

    except Exception as error:

        train_data = {
            "status": "error",
            "message": str(error)
        }


# ============================================================
# EMPTY RESPONSE
# ============================================================

if not train_data:

    st.error(
        "No response received from FastAPI."
    )

    st.info(
        """
        Start FastAPI:

        cd F:\\Train\\backend

        uvicorn main:app --reload
        """
    )

    st.stop()


# ============================================================
# ERROR RESPONSE
# ============================================================

if train_data.get("status") == "error":

    error_message = train_data.get(
        "message",
        "Unknown error"
    )

    st.session_state.connection_error = (
        error_message
    )

    st.error(
        f"WebSocket error: {error_message}"
    )

    st.info(
        """
        Check that:

        • FastAPI is running

        • WebSocket endpoint is available

        • Train number is valid

        • RailRadar API is available

        • ML model is loaded
        """
    )

    st.stop()


# ============================================================
# SAVE LIVE DATA
# ============================================================

st.session_state.last_update = train_data

st.session_state.connection_error = None

st.session_state.history.append(
    train_data
)


# Keep latest 100 records

if len(st.session_state.history) > 100:

    st.session_state.history = (
        st.session_state.history[-100:]
    )


history = st.session_state.history


# ============================================================
# EXTRACT DATA
# ============================================================

train_name = train_data.get(
    "train_name",
    "Unknown Train"
)

current_station = train_data.get(
    "current_station_name",
    train_data.get(
        "current_station",
        "Unknown"
    )
)

next_station = train_data.get(
    "next_station_name",
    train_data.get(
        "next_station",
        "Unknown"
    )
)

current_status = train_data.get(
    "current_status",
    "Unknown"
)

delay = float(
    train_data.get(
        "current_delay_min",
        0
    ) or 0
)

speed = float(
    train_data.get(
        "speed_kmh",
        0
    ) or 0
)

remaining_distance = float(
    train_data.get(
        "remaining_distance_km",
        0
    ) or 0
)

total_distance = float(
    train_data.get(
        "total_distance_km",
        0
    ) or 0
)

predicted_remaining = float(
    train_data.get(
        "predicted_remaining_minutes",
        0
    ) or 0
)

predicted_arrival = train_data.get(
    "predicted_arrival",
    "Unavailable"
)

predicted_delay = float(
    train_data.get(
        "predicted_delay_min",
        delay
    ) or 0
)

timestamp = train_data.get(
    "timestamp",
    datetime.now().astimezone().isoformat()
)


# ============================================================
# JOURNEY PROGRESS
# ============================================================

if total_distance > 0:

    distance_completed = (
        total_distance -
        remaining_distance
    )

    journey_progress = (
        distance_completed /
        total_distance
    ) * 100

else:

    distance_completed = 0

    journey_progress = 0


journey_progress = max(
    0,
    min(
        100,
        journey_progress
    )
)


# ============================================================
# TRAIN INFORMATION
# ============================================================

render_html(
    f"""
    <div class="info-box">

        <span class="train-name">
            🚆 {train_name}
        </span>

        <span class="separator">|</span>

        <span class="info-label">
            Train No
        </span>

        <span class="info-value">
            {train_number}
        </span>

        <span class="separator">|</span>

        <span class="info-label">
            Last Update
        </span>

        <span class="info-value">
            {timestamp}
        </span>

    </div>
    """
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


# ============================================================
# KPI 1
# ============================================================

with kpi1:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🚆 TRAIN
            </div>

            <div class="kpi-value">
                {train_number}
            </div>

            <div class="kpi-subtitle">
                {train_name}
            </div>

        </div>
        """
    )


# ============================================================
# KPI 2
# ============================================================

with kpi2:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                ⚠️ CURRENT DELAY
            </div>

            <div class="kpi-value">
                {delay:.0f} min
            </div>

            <div class="kpi-subtitle">
                Live operational delay
            </div>

        </div>
        """
    )


# ============================================================
# KPI 3
# ============================================================

with kpi3:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🏃 CURRENT SPEED
            </div>

            <div class="kpi-value">
                {speed:.1f} km/h
            </div>

            <div class="kpi-subtitle">
                Current train speed
            </div>

        </div>
        """
    )


# ============================================================
# KPI 4
# ============================================================

with kpi4:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                📍 REMAINING DISTANCE
            </div>

            <div class="kpi-value">
                {remaining_distance:.1f} km
            </div>

            <div class="kpi-subtitle">
                To destination
            </div>

        </div>
        """
    )


# ============================================================
# KPI 5
# ============================================================

with kpi5:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🧠 ML ETA
            </div>

            <div class="kpi-value">
                {predicted_remaining:.1f} min
            </div>

            <div class="kpi-subtitle">
                Predicted remaining time
            </div>

        </div>
        """
    )


# ============================================================
# LIVE OPERATIONS
# ============================================================

render_html(
    """
    <div class="section-title">
        📡 Live Operations
    </div>
    """
)


operation1, operation2, operation3, operation4 = (
    st.columns(4)
)


with operation1:

    st.metric(
        "Current Station",
        current_station
    )


with operation2:

    st.metric(
        "Next Station",
        next_station
    )


with operation3:

    st.metric(
        "Train Status",
        current_status
    )


with operation4:

    st.metric(
        "Predicted Delay",
        f"{predicted_delay:.1f} min"
    )


# ============================================================
# ML ETA ANALYSIS
# ============================================================

render_html(
    """
    <div class="section-title">
        🧠 ML ETA Analysis
    </div>
    """
)


eta_column, progress_column = st.columns(2)


# ============================================================
# ETA GAUGE
# ============================================================

with eta_column:

    st.plotly_chart(
        create_eta_gauge(
            predicted_remaining
        ),
        use_container_width=True
    )


# ============================================================
# JOURNEY PROGRESS
# ============================================================

with progress_column:

    st.plotly_chart(
        create_progress_chart(
            distance_completed,
            total_distance
        ),
        use_container_width=True
    )

    st.metric(
        "Journey Completed",
        f"{journey_progress:.1f}%"
    )


# ============================================================
# PREDICTED ARRIVAL
# ============================================================

render_html(
    """
    <div class="section-title">
        🕒 Predicted Arrival
    </div>
    """
)


arrival1, arrival2 = st.columns(2)


with arrival1:

    st.info(
        f"Predicted Arrival Time\n\n"
        f"{predicted_arrival}"
    )


with arrival2:

    st.info(
        f"Predicted Remaining Time\n\n"
        f"{predicted_remaining:.2f} minutes"
    )


# ============================================================
# REAL-TIME ANALYTICS
# ============================================================

render_html(
    """
    <div class="section-title">
        📊 Real-Time Analytics
    </div>
    """
)


chart1, chart2 = st.columns(2)


with chart1:

    st.plotly_chart(
        create_history_chart(history),
        use_container_width=True
    )


with chart2:

    st.plotly_chart(
        create_delay_chart(history),
        use_container_width=True
    )


# ============================================================
# LIVE HISTORY
# ============================================================

render_html(
    """
    <div class="section-title">
        📋 Live Prediction History
    </div>
    """
)


if history:

    table_data = []

    for row in reversed(history):

        table_data.append(
            {
                "Time": row.get(
                    "timestamp"
                ),

                "Current Station": row.get(
                    "current_station_name"
                ),

                "Next Station": row.get(
                    "next_station_name"
                ),

                "Delay (min)": row.get(
                    "current_delay_min"
                ),

                "Speed (km/h)": row.get(
                    "speed_kmh"
                ),

                "Remaining (km)": row.get(
                    "remaining_distance_km"
                ),

                "ML ETA (min)": row.get(
                    "predicted_remaining_minutes"
                ),

                "Predicted Arrival": row.get(
                    "predicted_arrival"
                )
            }
        )

    history_df = pd.DataFrame(
        table_data
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Waiting for live prediction history..."
    )


# ============================================================
# ML INFORMATION
# ============================================================

with st.expander(
    "🧠 ML Model Information"
):

    st.markdown(
        """
### Destination ETA Forecasting

The dashboard receives the current train state from
the FastAPI WebSocket and sends the current-state
features to the trained ETA model.

### Prediction Pipeline

```text
RailRadar Live Data
        ↓
Data Normalization
        ↓
Feature Engineering
        ↓
ML ETA Model
        ↓
Predicted Remaining Time
        ↓
Predicted Arrival""")