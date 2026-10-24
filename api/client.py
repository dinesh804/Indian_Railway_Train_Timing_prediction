import os
import requests
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("RAILRADAR_API_KEY")

BASE_URL = "https://api.railradar.in/v1/trains"


def get_live_train(train_number: str):

    url = f"{BASE_URL}/{train_number}/live"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()