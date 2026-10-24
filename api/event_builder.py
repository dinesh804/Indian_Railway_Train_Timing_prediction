import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "train_events.csv"


def extract_event(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        response = json.load(f)

    data = response["data"]

    train = data.get("train", {})
    current = data.get("currentLocation", {})
    next_halt = data.get("nextHalt", {})

    current_distance = current.get("distanceFromOriginKm", 0)
    total_distance = train.get("distance", 0)

    return {
        "timestamp": data.get("lastUpdatedAt"),

        "train_number": data.get("trainNumber"),
        "train_name": data.get("trainName"),

        "train_type": train.get("type"),
        "category": train.get("category"),

        "source_station": train.get("source", {}).get("code"),
        "destination_station": train.get("destination", {}).get("code"),

        "current_station": current.get("stationCode"),
        "current_station_name": current.get("stationName"),

        "current_status": current.get("status"),

        "current_delay_min": data.get("delayMinutes", 0),

        "speed_kmh": current.get("speedKmh", 0),

        "segment_progress": current.get("segmentProgress", 0),

        "distance_from_origin_km": current_distance,

        "remaining_distance_km": max(
            total_distance - current_distance,
            0
        ),

        "next_station": next_halt.get("stationCode"),
        "next_station_name": next_halt.get("stationName"),

        "next_station_distance_km": next_halt.get("distance"),

        "total_distance_km": total_distance,

        "total_halts": train.get("totalHalts"),

        "route_station_count": len(
            data.get("route", [])
        )
    }


def build_dataset():

    files = sorted(RAW_DIR.glob("*.json"))

    if not files:
        print("No raw JSON files found.")
        return

    rows = []

    for file in files:

        try:
            event = extract_event(file)
            rows.append(event)

        except Exception as e:
            print(f"Error processing {file.name}: {e}")

    if not rows:
        print("No valid events found.")
        return

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = list(rows[0].keys())

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("Dataset created successfully")
    print("--------------------------------")
    print(f"Raw files : {len(files)}")
    print(f"Events    : {len(rows)}")
    print(f"Output    : {OUTPUT_FILE}")


if __name__ == "__main__":
    build_dataset()
    