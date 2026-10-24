import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# ETA GAUGE
# ============================================================

def create_eta_gauge(eta_minutes):

    eta_minutes = float(eta_minutes or 0)

    max_value = max(
        600,
        eta_minutes * 1.2
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=eta_minutes,

            number={
                "suffix": " min",
                "font": {
                    "size": 32
                }
            },

            title={
                "text": "Predicted Remaining Time"
            },

            gauge={
                "axis": {
                    "range": [
                        0,
                        max_value
                    ]
                },

                "bar": {
                    "thickness": 0.3
                }
            }
        )
    )

    fig.update_layout(
        height=300,
        margin={
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20
        }
    )

    return fig


# ============================================================
# JOURNEY PROGRESS
# ============================================================

def create_progress_chart(
    remaining_distance,
    total_distance
):

    remaining_distance = float(
        remaining_distance or 0
    )

    total_distance = float(
        total_distance or 0
    )

    if total_distance > 0:

        progress = (
            remaining_distance
            / total_distance
        ) * 100

    else:

        progress = 0

    progress = max(
        0,
        min(100, progress)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[progress],
            y=["Journey"],
            orientation="h",

            text=[
                f"{progress:.1f}%"
            ],

            textposition="inside"
        )
    )

    fig.update_xaxes(
        range=[0, 100],
        title="Journey Progress (%)"
    )

    fig.update_layout(
        height=140,

        margin={
            "l": 20,
            "r": 20,
            "t": 20,
            "b": 40
        },

        showlegend=False
    )

    return fig


# ============================================================
# ETA HISTORY
# ============================================================

def create_history_chart(history):

    fig = go.Figure()

    if not history:

        fig.update_layout(
            title="Waiting for ETA history..."
        )

        return fig

    timestamps = [
        row.get("timestamp")
        for row in history
    ]

    eta_values = [
        float(
            row.get(
                "predicted_remaining_minutes",
                0
            ) or 0
        )
        for row in history
    ]

    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=eta_values,

            mode="lines+markers",

            name="Predicted ETA"
        )
    )

    fig.update_layout(
        title="ML ETA Trend",

        xaxis_title="Time",

        yaxis_title="Remaining Time (min)",

        height=350,

        hovermode="x unified"
    )

    return fig


# ============================================================
# DELAY HISTORY
# ============================================================

def create_delay_chart(history):

    if not history:

        fig = go.Figure()

        fig.update_layout(
            title="Waiting for delay history..."
        )

        return fig

    timestamps = [
        row.get("timestamp")
        for row in history
    ]

    delays = [
        float(
            row.get(
                "current_delay_min",
                0
            ) or 0
        )
        for row in history
    ]

    fig = px.area(
        x=timestamps,
        y=delays,

        labels={
            "x": "Time",
            "y": "Delay (minutes)"
        },

        title="Live Delay Trend"
    )

    fig.update_layout(
        height=350,
        hovermode="x unified"
    )

    return fig