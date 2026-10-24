import asyncio
import json
import websockets


TRAIN_NUMBER = "12653"

WS_URL = f"ws://127.0.0.1:8000/ws/train/{TRAIN_NUMBER}"


async def main():

    print("=" * 60)
    print("DYNAMIC TRAIN ETA - WEBSOCKET TEST")
    print("=" * 60)

    print(f"Connecting to train {TRAIN_NUMBER}...")
    print(f"WebSocket: {WS_URL}")

    try:

        async with websockets.connect(WS_URL) as websocket:

            print("\n✓ WebSocket connected")
            print("Waiting for live ETA updates...\n")

            while True:

                message = await websocket.recv()

                data = json.loads(message)

                if data.get("status") == "error":
                    print(
                        f"ERROR: {data.get('message')}"
                    )
                    continue

                print("-" * 60)

                print(
                    f"Timestamp       : "
                    f"{data.get('timestamp')}"
                )

                print(
                    f"Train           : "
                    f"{data.get('train_number')} - "
                    f"{data.get('train_name')}"
                )

                print(
                    f"Current         : "
                    f"{data.get('current_station_name')}"
                )

                print(
                    f"Next Station    : "
                    f"{data.get('next_station_name')}"
                )

                print(
                    f"Status          : "
                    f"{data.get('current_status')}"
                )

                print(
                    f"Delay           : "
                    f"{data.get('current_delay_min')} min"
                )

                print(
                    f"Speed           : "
                    f"{data.get('speed_kmh')} km/h"
                )

                print(
                    f"Remaining       : "
                    f"{data.get('remaining_distance_km')} km"
                )

                print(
                    f"ML Remaining    : "
                    f"{data.get('predicted_remaining_minutes')} min"
                )

                print(
                    f"Predicted ETA   : "
                    f"{data.get('predicted_arrival')}"
                )

                print(
                    f"Predicted Delay : "
                    f"{data.get('predicted_delay_min')} min"
                )

    except KeyboardInterrupt:

        print("\nWebSocket test stopped.")

    except Exception as error:

        print(
            f"\nWebSocket connection error: {error}"
        )


if __name__ == "__main__":
    asyncio.run(main())