import json
import time
from pathlib import Path
from datetime import datetime

from client import get_live_train
from normalizer import normalize_train_data


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"

TRAIN_NUMBER = "12653"

# Collect every 5 minutes
COLLECTION_INTERVAL = 300

# Safety limit
# Prevents accidentally consuming the API quota.
MAX_API_CALLS = 20


# ============================================================
# DIRECTORY
# ============================================================

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# COLLECT ONE SNAPSHOT
# ============================================================

def collect_once():

    print()
    print("=" * 60)
    print(f"Fetching train {TRAIN_NUMBER}")
    print("=" * 60)

    try:

        response = get_live_train(
            TRAIN_NUMBER
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        raw_file = (
            RAW_DIR
            / f"{TRAIN_NUMBER}_{timestamp}.json"
        )

        # Save complete API response
        with open(
            raw_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                response,
                file,
                indent=2,
                ensure_ascii=False
            )

        # Normalize
        normalized = normalize_train_data(
            response
        )

        print()
        print("TRAIN STATUS")
        print("-" * 40)

        print(
            f"Train          : "
            f"{normalized['train_number']}"
        )

        print(
            f"Name           : "
            f"{normalized['train_name']}"
        )

        print(
            f"Current        : "
            f"{normalized['current_station']} "
            f"({normalized['current_station_name']})"
        )

        print(
            f"Status         : "
            f"{normalized['current_status']}"
        )

        print(
            f"Delay          : "
            f"{normalized['current_delay_min']} min"
        )

        print(
            f"Speed          : "
            f"{normalized['speed_kmh']} km/h"
        )

        print(
            f"Distance       : "
            f"{normalized['distance_from_origin_km']} km"
        )

        print(
            f"Remaining      : "
            f"{normalized['remaining_distance_km']} km"
        )

        print(
            f"Next station   : "
            f"{normalized['next_station']} "
            f"({normalized['next_station_name']})"
        )

        print(
            f"Next distance  : "
            f"{normalized['next_station_distance_km']} km"
        )

        print(
            f"Timestamp      : "
            f"{normalized['timestamp']}"
        )

        print()
        print(
            f"Saved: {raw_file}"
        )

        return normalized

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        return None


# ============================================================
# JOURNEY COLLECTOR
# ============================================================

def run_collector():

    print()
    print("=" * 60)
    print("DYNAMIC ETA JOURNEY COLLECTOR")
    print("=" * 60)

    print(
        f"Train number      : {TRAIN_NUMBER}"
    )

    print(
        f"Interval          : "
        f"{COLLECTION_INTERVAL} seconds"
    )

    print(
        f"Maximum API calls : {MAX_API_CALLS}"
    )

    print()
    print(
        "Press Ctrl+C to stop safely."
    )

    call_count = 0

    try:

        while call_count < MAX_API_CALLS:

            call_count += 1

            print()
            print(
                f"API CALL "
                f"{call_count}/{MAX_API_CALLS}"
            )

            normalized = collect_once()

            if normalized is None:

                print(
                    "Collection failed."
                )

            else:

                status = (
                    normalized[
                        "current_status"
                    ]
                    or ""
                ).lower()

                # ------------------------------------------------
                # STOP CONDITIONS
                # ------------------------------------------------

                if status in [
                    "arrived",
                    "completed",
                    "terminated"
                ]:

                    print()
                    print(
                        "Train journey completed."
                    )

                    break

                # Some APIs may return destination
                # as current station.
                if (
                    normalized["current_station"]
                    == normalized[
                        "destination_station"
                    ]
                    and normalized[
                        "destination_station"
                    ] is not None
                ):

                    print()
                    print(
                        "Destination reached."
                    )

                    break

            # ----------------------------------------------------
            # WAIT
            # ----------------------------------------------------

            if call_count < MAX_API_CALLS:

                print()
                print(
                    f"Waiting "
                    f"{COLLECTION_INTERVAL} seconds..."
                )

                time.sleep(
                    COLLECTION_INTERVAL
                )

    except KeyboardInterrupt:

        print()
        print()
        print(
            "Collector stopped by user."
        )

    print()
    print("=" * 60)
    print("COLLECTION FINISHED")
    print("=" * 60)

    print(
        f"API calls used: {call_count}"
    )

    print(
        f"Raw data location: {RAW_DIR}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_collector()