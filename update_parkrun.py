# update_parkrun.py
import json
import datetime

data = {
    "last_updated": str(datetime.datetime.utcnow()),
    "volunteers": [
        {"name": "Alice", "events": 5},
        {"name": "Bob", "events": 3}
    ]
}

# Make sure the folder exists
import os
os.makedirs("data", exist_ok=True)

with open("data/parkrun.json", "w") as f:
    json.dump(data, f, indent=2)

print("Parkrun JSON updated!")
