import sys
from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "destination_eta_model.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading ETA model...")

model = joblib.load(
    MODEL_PATH
)

print(
    f"Model loaded: {MODEL_PATH}"
)


# ============================================================
# FEATURE PREPARATION
# ============================================================

def prepare_features(train_data):
    """
    Convert normalized live RailRadar data into
    the feature structure expected by the ETA model.
    """

    timestamp = pd.to_datetime(
        train_data["timestamp"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # TIME FEATURES
    # --------------------------------------------------------

    hour = timestamp.hour

    minute = timestamp.minute

    day_of_week = timestamp.dayofweek


    hour_sin = np.sin(
        2 * np.pi * hour / 24
    )

    hour_cos = np.cos(
        2 * np.pi * hour / 24
    )

    day_sin = np.sin(
        2 * np.pi * day_of_week / 7
    )

    day_cos = np.cos(
        2 * np.pi * day_of_week / 7
    )


    # --------------------------------------------------------
    # MODEL FEATURES
    # --------------------------------------------------------

    features = {

        "hour":
            hour,

        "minute":
            minute,

        "day_of_week":
            day_of_week,

        "hour_sin":
            hour_sin,

        "hour_cos":
            hour_cos,

        "day_sin":
            day_sin,

        "day_cos":
            day_cos,

        "current_delay_min":
            train_data.get(
                "current_delay_min",
                0
            ),

        "speed_kmh":
            train_data.get(
                "speed_kmh",
                0
            ),

        "distance_from_origin_km":
            train_data.get(
                "distance_from_origin_km",
                0
            ),

        "remaining_distance_km":
            train_data.get(
                "remaining_distance_km",
                0
            ),

        "next_station_distance_km":
            train_data.get(
                "next_station_distance_km",
                0
            ),

        "segment_progress":
            train_data.get(
                "segment_progress",
                0
            ),

        "total_distance_km":
            train_data.get(
                "total_distance_km",
                0
            ),

        "total_halts":
            train_data.get(
                "total_halts",
                0
            ),

        "current_station":
            train_data.get(
                "current_station",
                ""
            ),

        "next_station":
            train_data.get(
                "next_station",
                ""
            ),

        "train_type":
            train_data.get(
                "train_type",
                ""
            ),

        "category":
            train_data.get(
                "category",
                ""
            )
    }


    return pd.DataFrame(
        [features]
    )


# ============================================================
# ETA PREDICTION
# ============================================================

def predict_eta(train_data):

    """
    Predict remaining travel time and destination ETA.
    """

    # --------------------------------------------------------
    # PREPARE FEATURES
    # --------------------------------------------------------

    X = prepare_features(
        train_data
    )


    # --------------------------------------------------------
    # ML PREDICTION
    # --------------------------------------------------------

    predicted_minutes = model.predict(
        X
    )[0]


    predicted_minutes = max(
        float(predicted_minutes),
        0
    )


    # --------------------------------------------------------
    # CURRENT TIMESTAMP
    # --------------------------------------------------------

    current_timestamp = pd.to_datetime(
        train_data["timestamp"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # DESTINATION ETA
    # --------------------------------------------------------

    predicted_arrival = (
        current_timestamp
        + pd.Timedelta(
            minutes=predicted_minutes
        )
    )


    # --------------------------------------------------------
    # EXPECTED DELAY
    # --------------------------------------------------------

    current_delay = float(
        train_data.get(
            "current_delay_min",
            0
        )
    )


    # Approximate predicted delay.
    #
    # This is currently a derived operational estimate,
    # not a separately trained delay model.

    predicted_delay = max(
        current_delay,
        0
    )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result = {

        "train_number":
            train_data.get(
                "train_number"
            ),

        "train_name":
            train_data.get(
                "train_name"
            ),

        "current_station":
            train_data.get(
                "current_station"
            ),

        "current_station_name":
            train_data.get(
                "current_station_name"
            ),

        "next_station":
            train_data.get(
                "next_station"
            ),

        "next_station_name":
            train_data.get(
                "next_station_name"
            ),

        "destination":
            train_data.get(
                "destination_station"
            ),

        "current_delay_min":
            round(
                current_delay,
                2
            ),

        "speed_kmh":
            round(
                float(
                    train_data.get(
                        "speed_kmh",
                        0
                    )
                ),
                2
            ),

        "remaining_distance_km":
            round(
                float(
                    train_data.get(
                        "remaining_distance_km",
                        0
                    )
                ),
                2
            ),

        "predicted_remaining_minutes":
            round(
                predicted_minutes,
                2
            ),

        "predicted_arrival":
            predicted_arrival.isoformat(),

        "predicted_delay_min":
            round(
                predicted_delay,
                2
            ),

        "prediction_timestamp":
            datetime.now().isoformat()
    }


    return result


# ============================================================
# TEST FUNCTION
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("ETA ENGINE TEST")
    print("=" * 70)


    # Example live normalized data.
    #
    # This structure matches api/normalizer.py.

    sample_data = {

        "timestamp":
            "2026-09-30T23:09:01+05:30",

        "train_number":
            "12653",

        "train_name":
            "Rock Fort SF Express",

        "train_type":
            "Superfast Express",

        "category":
            "Express",

        "source_station":
            "MS",

        "destination_station":
            "TPJ",

        "current_station":
            "MS",

        "current_station_name":
            "Chennai Egmore",

        "current_status":
            "at-station",

        "current_delay_min":
            0,

        "speed_kmh":
            0,

        "segment_progress":
            0,

        "distance_from_origin_km":
            0,

        "remaining_distance_km":
            336.9,

        "next_station":
            "MBM",

        "next_station_name":
            "Mambalam",

        "next_station_distance_km":
            6.8,

        "total_distance_km":
            336.9,

        "total_halts":
            13
    }


    try:

        result = predict_eta(
            sample_data
        )


        print(
            "\nPrediction Result"
        )

        print(
            "-" * 70
        )


        for key, value in result.items():

            print(
                f"{key}: {value}"
            )


    except Exception as error:

        print(
            "\nERROR:"
        )

        print(error)