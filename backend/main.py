import sys
import asyncio
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

API_DIR = BASE_DIR / "api"
ETA_ENGINE_DIR = BASE_DIR / "eta_engine"


# Add project folders to Python import path
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(ETA_ENGINE_DIR))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from client import get_live_train
from normalizer import normalize_train_data
from predictor import predict_eta


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Dynamic Train ETA Forecasting System",
    description="Live railway ETA prediction using Machine Learning",
    version="1.0.0"
)


# ============================================================
# DEFAULT TRAIN
# ============================================================

DEFAULT_TRAIN_NUMBER = "12653"


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "system": "Dynamic Train ETA Forecasting System",
        "status": "running",
        "train": DEFAULT_TRAIN_NUMBER,
        "architecture": [
            "RailRadar API",
            "Data Normalization",
            "ML ETA Engine",
            "FastAPI",
            "WebSocket"
        ]
    }


# ============================================================
# TRAIN ETA PIPELINE
# ============================================================

def get_train_prediction(train_number: str):

    # --------------------------------------------------------
    # STEP 1: Get live train data from RailRadar API
    # --------------------------------------------------------

    response = get_live_train(train_number)

    # --------------------------------------------------------
    # STEP 2: Normalize API response
    # --------------------------------------------------------

    train_data = normalize_train_data(response)

    # --------------------------------------------------------
    # STEP 3: Generate ML ETA prediction
    # --------------------------------------------------------

    prediction = predict_eta(train_data)

    # --------------------------------------------------------
    # STEP 4: Combine live information + ML prediction
    # --------------------------------------------------------

    result = {
        "timestamp": datetime.now().astimezone().isoformat(),

        # Train information
        "train_number": train_data.get("train_number"),
        "train_name": train_data.get("train_name"),

        # Current location
        "current_station": train_data.get("current_station"),
        "current_station_name": train_data.get("current_station_name"),

        # Next station
        "next_station": train_data.get("next_station"),
        "next_station_name": train_data.get("next_station_name"),

        # Current operational information
        "current_status": train_data.get("current_status"),
        "current_delay_min": train_data.get("current_delay_min"),
        "speed_kmh": train_data.get("speed_kmh"),

        # Distance information
        "distance_from_origin_km": train_data.get(
            "distance_from_origin_km"
        ),

        "remaining_distance_km": train_data.get(
            "remaining_distance_km"
        ),

        "next_station_distance_km": train_data.get(
            "next_station_distance_km"
        ),

        "total_distance_km": train_data.get(
            "total_distance_km"
        ),

        # ML prediction
        "predicted_remaining_minutes": prediction.get(
            "predicted_remaining_minutes"
        ),

        "predicted_arrival": prediction.get(
            "predicted_arrival"
        ),

        "predicted_delay_min": prediction.get(
            "predicted_delay_min"
        )
    }

    return result


# ============================================================
# REST API ENDPOINT
# ============================================================

@app.get("/train/{train_number}")
def train_prediction(train_number: str):

    try:

        result = get_train_prediction(train_number)

        return {
            "status": "success",
            "data": result
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# ============================================================
# WEBSOCKET ENDPOINT
# ============================================================

@app.websocket("/ws/train/{train_number}")
async def train_websocket(
    websocket: WebSocket,
    train_number: str
):

    await websocket.accept()

    print(
        f"\nWebSocket connected "
        f"for train {train_number}"
    )

    try:

        while True:

            try:

                # ------------------------------------------------
                # Fetch live data + predict ETA
                # ------------------------------------------------

                result = get_train_prediction(
                    train_number
                )

                # ------------------------------------------------
                # Send result to connected dashboard
                # ------------------------------------------------

                await websocket.send_json(result)

                print(
                    "\nETA UPDATE"
                    f"\nTrain       : {result['train_number']}"
                    f"\nCurrent     : {result['current_station_name']}"
                    f"\nNext        : {result['next_station_name']}"
                    f"\nDelay       : {result['current_delay_min']} min"
                    f"\nSpeed       : {result['speed_kmh']} km/h"
                    f"\nRemaining   : {result['remaining_distance_km']} km"
                    f"\nML ETA      : {result['predicted_arrival']}"
                    f"\n"
                )

            except Exception as error:

                print(
                    f"\nPrediction error: {error}"
                )

                await websocket.send_json(
                    {
                        "status": "error",
                        "message": str(error)
                    }
                )

            # ----------------------------------------------------
            # Wait before next live API request
            #
            # Development interval = 60 seconds
            #
            # NOTE:
            # RailRadar has API request limits.
            # Do not continuously poll at 60 seconds in production.
            # ----------------------------------------------------

            await asyncio.sleep(60)

    except WebSocketDisconnect:

        print(
            f"\nWebSocket disconnected "
            f"for train {train_number}"
        )

    except Exception as error:

        print(
            f"\nWebSocket error: {error}"
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "Dynamic Train ETA Forecasting System",
        "ml_engine": "active",
        "websocket": "available"
    }