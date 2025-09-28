import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

url = "https://www.parkrun.org.uk/parkrunner/2305995/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

table = soup.find("table", {"id": "volunteer-history"})
if not table:
    raise ValueError("Volunteer history table not found in HTML")

data = []
total_credits = 0

for row in table.select("tbody tr"):
    cols = row.find_all("td")
    role = cols[0].text.strip()
    try:
        occasions = int(cols[1].text.strip())
    except ValueError:
        occasions = 0
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

print("✅ Parkrun volunteer data updated successfully")
