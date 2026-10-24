import json
import random
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "synthetic_training_dataset.csv"
)

TRAIN_NUMBER = "12653"

# Number of simulated journeys
NUM_JOURNEYS = 100

# Observation interval
INTERVAL_MINUTES = 5

# Reproducibility
RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# ============================================================
# LOAD REAL API ROUTE
# ============================================================

def load_route():

    files = sorted(
        RAW_DIR.glob("*.json")
    )

    if not files:
        raise FileNotFoundError(
            "No raw API JSON files found."
        )

    # Use the latest API response
    latest_file = files[-1]

    print(
        f"Using route from: {latest_file.name}"
    )

    with open(
        latest_file,
        "r",
        encoding="utf-8"
    ) as f:

        response = json.load(f)

    data = response.get(
        "data",
        {}
    )

    train = data.get(
        "train",
        {}
    )

    route = data.get(
        "route",
        []
    )

    if not route:
        raise ValueError(
            "No route information found "
            "in the API response."
        )

    return train, route


# ============================================================
# SAFE FLOAT CONVERSION
# ============================================================

def safe_float(
    value,
    default=0
):

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


# ============================================================
# CREATE ONE SYNTHETIC JOURNEY
# ============================================================

def generate_journey(
    journey_id,
    train,
    route
):

    rows = []

    if not route:
        return rows

    # --------------------------------------------------------
    # INITIAL DELAY
    # --------------------------------------------------------

    initial_delay = random.choice([
        0,
        0,
        0,
        0,
        2,
        3,
        5,
        8,
        10,
        15,
        20,
        30
    ])

    current_delay = initial_delay

    # --------------------------------------------------------
    # JOURNEY START TIME
    # --------------------------------------------------------

    start_time = (
        datetime(
            2026,
            1,
            1,
            20,
            0
        )
        + timedelta(
            days=journey_id
        )
    )

    # --------------------------------------------------------
    # TOTAL DISTANCE
    # --------------------------------------------------------

    total_distance = safe_float(
        train.get(
            "distance"
        )
    )

    # --------------------------------------------------------
    # GENERATE OBSERVATIONS
    # --------------------------------------------------------

    for i, station in enumerate(route):

        # ----------------------------------------------------
        # STATION INFORMATION
        # ----------------------------------------------------

        station_code = station.get(
            "stationCode"
        )

        station_name = station.get(
            "stationName"
        )

        distance = safe_float(
            station.get(
                "distance"
            )
        )

        # ----------------------------------------------------
        # SPEED
        # ----------------------------------------------------

        if i == 0:

            speed = 0

        else:

            # Normal operating speed
            speed = random.uniform(
                50,
                100
            )

            # Occasionally simulate
            # slower operational conditions
            if random.random() < 0.12:

                speed = random.uniform(
                    25,
                    50
                )

        # ----------------------------------------------------
        # DELAY DYNAMICS
        # ----------------------------------------------------

        if i > 0:

            event = random.random()

            # =================================================
            # NORMAL OPERATION
            # =================================================

            if event < 0.60:

                # Small natural variation
                delay_change = random.choice([
                    -2,
                    -1,
                    0,
                    0,
                    0,
                    1
                ])

                current_delay += (
                    delay_change
                )

            # =================================================
            # SMALL OPERATIONAL DELAY
            # =================================================

            elif event < 0.82:

                delay_increase = random.randint(
                    1,
                    3
                )

                current_delay += (
                    delay_increase
                )

            # =================================================
            # MODERATE DISRUPTION
            # =================================================

            elif event < 0.95:

                delay_increase = random.randint(
                    3,
                    8
                )

                current_delay += (
                    delay_increase
                )

            # =================================================
            # MAJOR DISRUPTION
            # =================================================

            else:

                delay_increase = random.randint(
                    8,
                    15
                )

                current_delay += (
                    delay_increase
                )

            # =================================================
            # DELAY RECOVERY
            # =================================================

            # When a train has accumulated delay,
            # sometimes it can recover some time.

            if current_delay > 10:

                if random.random() < 0.30:

                    recovery = random.randint(
                        2,
                        6
                    )

                    current_delay -= recovery

            # =================================================
            # BOUNDARIES
            # =================================================

            # Delay cannot be negative.
            current_delay = max(
                current_delay,
                0
            )

            # Prevent unrealistic runaway delay.
            current_delay = min(
                current_delay,
                90
            )

        # ----------------------------------------------------
        # SEGMENT PROGRESS
        # ----------------------------------------------------

        if i == 0:

            segment_progress = 0

        else:

            segment_progress = random.uniform(
                0.1,
                1.0
            )

        # ----------------------------------------------------
        # REMAINING DISTANCE
        # ----------------------------------------------------

        remaining_distance = max(
            total_distance - distance,
            0
        )

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = (
            start_time
            + timedelta(
                minutes=(
                    i
                    * INTERVAL_MINUTES
                )
            )
        )

        # ----------------------------------------------------
        # NEXT STATION
        # ----------------------------------------------------

        if i + 1 < len(route):

            next_station = route[
                i + 1
            ]

            next_station_code = (
                next_station.get(
                    "stationCode"
                )
            )

            next_station_name = (
                next_station.get(
                    "stationName"
                )
            )

            next_station_distance = (
                safe_float(
                    next_station.get(
                        "distance"
                    )
                )
                - distance
            )

            next_station_distance = max(
                next_station_distance,
                0
            )

        else:

            next_station_code = None

            next_station_name = None

            next_station_distance = 0

        # ----------------------------------------------------
        # CREATE OBSERVATION
        # ----------------------------------------------------

        rows.append({

            # Journey
            "journey_id":
                journey_id,

            # Time
            "timestamp":
                timestamp,

            "hour":
                timestamp.hour,

            "day_of_week":
                timestamp.weekday(),

            # Train
            "train_number":
                TRAIN_NUMBER,

            "train_name":
                train.get(
                    "name"
                ),

            "train_type":
                train.get(
                    "type"
                ),

            "category":
                train.get(
                    "category"
                ),

            # Current station
            "current_station":
                station_code,

            "current_station_name":
                station_name,

            # Current operational state
            "current_delay_min":
                round(
                    current_delay,
                    2
                ),

            "speed_kmh":
                round(
                    speed,
                    2
                ),

            "segment_progress":
                round(
                    segment_progress,
                    3
                ),

            # Distance
            "distance_from_origin_km":
                round(
                    distance,
                    2
                ),

            "remaining_distance_km":
                round(
                    remaining_distance,
                    2
                ),

            # Next station
            "next_station":
                next_station_code,

            "next_station_name":
                next_station_name,

            "next_station_distance_km":
                round(
                    next_station_distance,
                    2
                ),

            # Route
            "total_distance_km":
                round(
                    total_distance,
                    2
                ),

            "total_halts":
                train.get(
                    "totalHalts"
                ),

            # These are created after the
            # complete journey is generated.
            "future_delay_min":
                None,

            "future_timestamp":
                None,

            "forecast_horizon_min":
                None
        })

    return rows


# ============================================================
# CREATE FUTURE TARGETS
# ============================================================

def create_future_targets(
    df
):

    print()
    print(
        "Creating future-delay targets..."
    )

    # --------------------------------------------------------
    # SORT BY JOURNEY AND TIME
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "journey_id",
            "timestamp"
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # FUTURE DELAY
    # --------------------------------------------------------

    # The target is the actual simulated delay
    # at the next observation.

    df["future_delay_min"] = (
        df.groupby(
            "journey_id"
        )[
            "current_delay_min"
        ].shift(-1)
    )

    # --------------------------------------------------------
    # FUTURE TIMESTAMP
    # --------------------------------------------------------

    df["future_timestamp"] = (
        df.groupby(
            "journey_id"
        )[
            "timestamp"
        ].shift(-1)
    )

    # --------------------------------------------------------
    # FORECAST HORIZON
    # --------------------------------------------------------

    df["forecast_horizon_min"] = (
        (
            df["future_timestamp"]
            - df["timestamp"]
        ).dt.total_seconds()
        / 60
    )

    # --------------------------------------------------------
    # REMOVE LAST OBSERVATION
    # --------------------------------------------------------

    # The final observation of each journey
    # has no future observation.

    df = df.dropna(
        subset=[
            "future_delay_min",
            "future_timestamp",
            "forecast_horizon_min"
        ]
    )

    # --------------------------------------------------------
    # VALID FORECAST HORIZON
    # --------------------------------------------------------

    df = df[
        df[
            "forecast_horizon_min"
        ] > 0
    ]

    return df.reset_index(
        drop=True
    )


# ============================================================
# DATA VALIDATION
# ============================================================

def validate_dataset(
    df
):

    print()
    print(
        "=" * 60
    )

    print(
        "DATASET VALIDATION"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Total rows       : "
        f"{len(df)}"
    )

    print(
        f"Journeys         : "
        f"{df['journey_id'].nunique()}"
    )

    print(
        f"Train number     : "
        f"{df['train_number'].nunique()}"
    )

    print()

    # --------------------------------------------------------
    # CURRENT DELAY
    # --------------------------------------------------------

    print(
        "Current delay:"
    )

    print(
        df[
            "current_delay_min"
        ].describe()
    )

    print()

    # --------------------------------------------------------
    # FUTURE DELAY
    # --------------------------------------------------------

    print(
        "Future delay:"
    )

    print(
        df[
            "future_delay_min"
        ].describe()
    )

    print()

    # --------------------------------------------------------
    # SPEED
    # --------------------------------------------------------

    print(
        "Speed:"
    )

    print(
        df[
            "speed_kmh"
        ].describe()
    )

    print()

    # --------------------------------------------------------
    # FORECAST HORIZON
    # --------------------------------------------------------

    print(
        "Forecast horizon:"
    )

    print(
        df[
            "forecast_horizon_min"
        ].describe()
    )

    print()

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    missing = (
        df.isnull()
        .sum()
    )

    missing = missing[
        missing > 0
    ]

    if len(missing) == 0:

        print(
            "Missing values: NONE"
        )

    else:

        print(
            "Missing values:"
        )

        print(
            missing
        )

    # --------------------------------------------------------
    # DELAY RANGE CHECK
    # --------------------------------------------------------

    print()

    print(
        "Delay range check:"
    )

    max_delay = df[
        "current_delay_min"
    ].max()

    if max_delay <= 90:

        print(
            "PASS - maximum delay is "
            f"{max_delay:.2f} minutes"
        )

    else:

        print(
            "WARNING - maximum delay is "
            f"{max_delay:.2f} minutes"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print(
        "=" * 60
    )

    print(
        "SYNTHETIC RAILWAY DATA GENERATOR"
    )

    print(
        "=" * 60
    )

    print()

    # --------------------------------------------------------
    # LOAD REAL API ROUTE
    # --------------------------------------------------------

    train, route = load_route()

    print(
        f"Train          : "
        f"{TRAIN_NUMBER}"
    )

    print(
        f"Route stations : "
        f"{len(route)}"
    )

    print(
        f"Journeys       : "
        f"{NUM_JOURNEYS}"
    )

    print(
        f"Interval       : "
        f"{INTERVAL_MINUTES} minutes"
    )

    print()

    # --------------------------------------------------------
    # GENERATE JOURNEYS
    # --------------------------------------------------------

    all_rows = []

    for journey_id in range(
        1,
        NUM_JOURNEYS + 1
    ):

        journey_rows = (
            generate_journey(
                journey_id,
                train,
                route
            )
        )

        all_rows.extend(
            journey_rows
        )

    print(
        f"Raw observations generated: "
        f"{len(all_rows)}"
    )

    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(
        all_rows
    )

    # --------------------------------------------------------
    # FUTURE TARGET
    # --------------------------------------------------------

    df = create_future_targets(
        df
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "journey_id",
            "timestamp"
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validate_dataset(
        df
    )

    # --------------------------------------------------------
    # FINAL INFORMATION
    # --------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "SYNTHETIC DATA CREATED SUCCESSFULLY"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Rows       : "
        f"{len(df)}"
    )

    print(
        f"Journeys   : "
        f"{df['journey_id'].nunique()}"
    )

    print(
        f"Output     : "
        f"{OUTPUT_FILE}"
    )

    print()

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    print(
        "First 10 observations:"
    )

    print()

    print(
        df.head(10).to_string(
            index=False
        )
    )

    print()

    print(
        "=" * 60
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()