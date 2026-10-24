# ============================================================
# WEBSOCKET CLIENT
# Dynamic Train ETA Forecasting System
# ============================================================

import asyncio
import json
import websockets


# ============================================================
# RECEIVE TRAIN UPDATE
# ============================================================

async def receive_train_update(train_number: str):

    websocket_url = (
        f"ws://127.0.0.1:8000/ws/train/{train_number}"
    )

    try:

        async with websockets.connect(
            websocket_url,
            open_timeout=30
        ) as websocket:

            message = await asyncio.wait_for(
                websocket.recv(),
                timeout=30
            )

            data = json.loads(message)

            return data

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# ============================================================
# STREAMLIT-SAFE FUNCTION
# ============================================================

def get_train_update(train_number: str):

    try:

        return asyncio.run(
            receive_train_update(train_number)
        )

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }