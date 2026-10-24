from datetime import datetime


def normalize_train_data(api_response):

    data = api_response["data"]

    train = data["train"]
    current = data.get("currentLocation", {})
    next_halt = data.get("nextHalt", {})

    route = data.get("route", [])

    current_distance = current.get(
        "distanceFromOriginKm", 0
    )

    total_distance = train.get(
        "distance", 0
    )

    remaining_distance = max(
        total_distance - current_distance,
        0
    )

    return {
        "timestamp": data.get("lastUpdatedAt"),

        "train_number": data.get("trainNumber"),

        "train_name": data.get("trainName"),

        "train_type": train.get("type"),

        "category": train.get("category"),

        "source_station": train.get(
            "source", {}
        ).get("code"),

        "destination_station": train.get(
            "destination", {}
        ).get("code"),

        "current_station": current.get(
            "stationCode"
        ),

        "current_station_name": current.get(
            "stationName"
        ),

        "current_status": current.get(
            "status"
        ),

        "current_delay_min": data.get(
            "delayMinutes", 0
        ),

        "speed_kmh": current.get(
            "speedKmh", 0
        ),

        "segment_progress": current.get(
            "segmentProgress", 0
        ),

        "distance_from_origin_km": current_distance,

        "remaining_distance_km": remaining_distance,

        "next_station": next_halt.get(
            "stationCode"
        ),

        "next_station_name": next_halt.get(
            "stationName"
        ),

        "next_station_distance_km": next_halt.get(
            "distance"
        ),

        "total_distance_km": total_distance,

        "total_halts": train.get(
            "totalHalts"
        ),

        "route_station_count": len(route)
    }