import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
EVENTS_FILE = BASE_DIR / "data" / "train_events.csv"
OUTPUT_FILE = BASE_DIR / "data" / "training_dataset.csv"


# --------------------------------------------------
# LOAD RAW API SNAPSHOTS
# --------------------------------------------------

def load_snapshots():

    records = []

    files = sorted(RAW_DIR.glob("*.json"))

    print(f"Found {len(files)} raw JSON files")

    for file in files:

        try:

            with open(file, "r", encoding="utf-8") as f:
                response = json.load(f)

            data = response.get("data", {})

            records.append({
                "file": file.name,
                "timestamp": data.get("lastUpdatedAt"),
                "train_number": data.get("trainNumber"),
                "delay_minutes": data.get("delayMinutes", 0),
                "current_location": data.get(
                    "currentLocation", {}
                ),
                "next_halt": data.get(
                    "nextHalt", {}
                ),
                "train": data.get(
                    "train", {}
                ),
                "route": data.get(
                    "route", []
                )
            })

        except Exception as error:

            print(
                f"Could not process {file.name}: {error}"
            )

    return records


# --------------------------------------------------
# EXTRACT CURRENT TRAIN FEATURES
# --------------------------------------------------

def create_feature_rows(records):

    rows = []

    for record in records:

        current = record["current_location"]
        next_halt = record["next_halt"]
        train = record["train"]

        total_distance = train.get(
            "distance", 0
        )

        current_distance = current.get(
            "distanceFromOriginKm", 0
        )

        remaining_distance = max(
            total_distance - current_distance,
            0
        )

        timestamp = pd.to_datetime(
            record["timestamp"],
            errors="coerce"
        )

        rows.append({

            # Time
            "timestamp": timestamp,

            "hour": (
                timestamp.hour
                if pd.notna(timestamp)
                else None
            ),

            "day_of_week": (
                timestamp.dayofweek
                if pd.notna(timestamp)
                else None
            ),

            # Train
            "train_number": record[
                "train_number"
            ],

            "train_type": train.get(
                "type"
            ),

            "category": train.get(
                "category"
            ),

            # Current state
            "current_station": current.get(
                "stationCode"
            ),

            "current_status": current.get(
                "status"
            ),

            "current_delay_min": record[
                "delay_minutes"
            ],

            "speed_kmh": current.get(
                "speedKmh", 0
            ),

            "segment_progress": current.get(
                "segmentProgress", 0
            ),

            "distance_from_origin_km":
                current_distance,

            "remaining_distance_km":
                remaining_distance,

            # Next station
            "next_station": next_halt.get(
                "stationCode"
            ),

            "next_station_distance_km":
                next_halt.get("distance"),

            # Train route
            "total_distance_km":
                total_distance,

            "total_halts": train.get(
                "totalHalts"
            )
        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# CREATE FUTURE DELAY TARGET
# --------------------------------------------------

def create_target(df):

    if df.empty:
        return df

    df = df.sort_values(
        [
            "train_number",
            "timestamp"
        ]
    ).reset_index(drop=True)

    # Future observed delay
    df["future_delay_min"] = (
        df.groupby("train_number")[
            "current_delay_min"
        ].shift(-1)
    )

    # How many minutes into the future
    df["future_timestamp"] = (
        df.groupby("train_number")[
            "timestamp"
        ].shift(-1)
    )

    df["forecast_horizon_min"] = (
        (
            df["future_timestamp"]
            - df["timestamp"]
        ).dt.total_seconds()
        / 60
    )

    return df


# --------------------------------------------------
# REMOVE INVALID TARGET ROWS
# --------------------------------------------------

def clean_training_data(df):

    if df.empty:
        return df

    # We need an observed future value.
    df = df.dropna(
        subset=[
            "future_delay_min",
            "forecast_horizon_min"
        ]
    )

    # Ignore impossible horizons.
    df = df[
        df["forecast_horizon_min"] > 0
    ]

    # Sort again.
    df = df.sort_values(
        [
            "train_number",
            "timestamp"
        ]
    )

    return df.reset_index(drop=True)


# --------------------------------------------------
# SAVE DATASET
# --------------------------------------------------

def main():

    print()
    print("=" * 60)
    print("DYNAMIC ETA - TRAINING DATA PREPARATION")
    print("=" * 60)

    records = load_snapshots()

    if not records:

        print()
        print("No raw snapshots found.")
        return

    print()
    print("Creating feature dataset...")

    df = create_feature_rows(records)

    print(
        f"Feature rows created: {len(df)}"
    )

    df = create_target(df)

    print(
        f"Rows after target generation: {len(df)}"
    )

    training_df = clean_training_data(df)

    print(
        f"Valid training rows: {len(training_df)}"
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    training_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Training dataset saved:")
    print(OUTPUT_FILE)

    print()
    print("Columns:")
    for column in training_df.columns:
        print(f"  - {column}")

    print()
    print("Preview:")

    if training_df.empty:

        print(
            "No training rows yet."
        )

        print()
        print(
            "This is expected when only "
            "one or two snapshots exist."
        )

    else:

        print(
            training_df.head().to_string(
                index=False
            )
        )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()