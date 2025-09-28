import requests
import json
from datetime import datetime

url = "https://www.parkrun.org.uk/parkrunner/2305995/volunteer-history/json/"
r = requests.get(url)
r.raise_for_status()
volunteers = r.json()

data = []
total_credits = 0
for item in volunteers:
    role = item["Role"]
    occasions = item["Occasions"]
    data.append({"role": role, "occasions": occasions})
    total_credits += occasions

data.append({"role": "Total Credits", "occasions": total_credits})

result = {
    "source": "parkrun 2305995",
    "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
    "data": data
}

with open("data/parkrun.json", "w") as f:
    json.dump(result, f, indent=2)
