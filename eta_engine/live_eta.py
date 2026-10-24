from pathlib import Path
import sys

# Allow importing modules from api/
BASE_DIR = Path(__file__).resolve().parent.parent
API_DIR = BASE_DIR / "api"

sys.path.insert(0, str(API_DIR))

from client import get_live_train
from normalizer import normalize_train_data

from predictor import predict_eta


TRAIN_NUMBER = "12653"


def get_live_eta(train_number: str):

    print("=" * 70)
    print("LIVE TRAIN ETA")
    print("=" * 70)

    print(
        f"\nFetching live data for train {train_number}..."
    )

    # --------------------------------------------------------
    # 1. GET LIVE RAILRADAR DATA
    # --------------------------------------------------------

    response = get_live_train(
        train_number
    )

    # --------------------------------------------------------
    # 2. NORMALIZE API RESPONSE
    # --------------------------------------------------------

    normalized = normalize_train_data(
        response
    )

    # --------------------------------------------------------
    # 3. ML ETA PREDICTION
    # --------------------------------------------------------

    prediction = predict_eta(
        normalized
    )

    return normalized, prediction


if __name__ == "__main__":

    try:

        normalized, prediction = (
            get_live_eta(
                TRAIN_NUMBER
            )
        )

        print(
            "\n" + "=" * 70
        )

        print(
            "LIVE TRAIN INFORMATION"
        )

        print(
            "=" * 70
        )

        print(
            f"Train       : "
            f"{normalized['train_number']}"
        )

        print(
            f"Name        : "
            f"{normalized['train_name']}"
        )

        print(
            f"Status      : "
            f"{normalized['current_status']}"
        )

        print(
            f"Current     : "
            f"{normalized['current_station_name']} "
            f"({normalized['current_station']})"
        )

        print(
            f"Next        : "
            f"{normalized['next_station_name']} "
            f"({normalized['next_station']})"
        )

        print(
            f"Delay       : "
            f"{normalized['current_delay_min']} min"
        )

        print(
            f"Speed       : "
            f"{normalized['speed_kmh']} km/h"
        )

        print(
            f"Remaining   : "
            f"{normalized['remaining_distance_km']} km"
        )


        print(
            "\n" + "=" * 70
        )

        print(
            "ML ETA PREDICTION"
        )

        print(
            "=" * 70
        )

        print(
            f"Predicted remaining time : "
            f"{prediction['predicted_remaining_minutes']:.2f} min"
        )

        print(
            f"Predicted arrival        : "
            f"{prediction['predicted_arrival']}"
        )

        print(
            f"Predicted delay          : "
            f"{prediction['predicted_delay_min']:.2f} min"
        )


        print(
            "\n" + "=" * 70
        )

        print(
            "LIVE ETA PIPELINE SUCCESS"
        )

        print(
            "=" * 70
        )


    except Exception as error:

        print(
            "\nERROR:"
        )

        print(
            str(error)
        )