import json
from pathlib import Path 

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_tickets.json"

def load_tickets() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)