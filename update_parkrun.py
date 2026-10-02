import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://www.parkrun.org.uk/parkrunner/2305995/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def main():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return

    # Check for Cloudflare challenge string
    if "Let's confirm you are human" in response.text:
        print("Cloudflare verification challenge encountered.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the Volunteer Summary heading
    heading = soup.find("h3", id="volunteer-summary")
    if not heading:
        print("Volunteer Summary heading not found.")
        return

    # Locate table within parent container
    parent = heading.parent
    volunteer_table = parent.find("table") if parent else None
    if not volunteer_table:
        print("Volunteer Summary table not found.")
        return

    volunteer_data = []

    # Extract tbody rows
    tbody = volunteer_table.find("tbody")
    if tbody:
        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 2:
                role = cols[0].get_text(strip=True)
                try:
                    occasions = int(cols[1].get_text(strip=True))
                except ValueError:
                    occasions = 0
                volunteer_data.append({"role": role, "occasions": occasions})

    if not volunteer_data:
        print("No volunteer data rows found.")
        return

    # Extract total credits from tfoot or sum
    tfoot_credit = volunteer_table.select_one("tfoot tr td:last-child")
    if tfoot_credit and tfoot_credit.get_text(strip=True).isdigit():
        total_credits = int(tfoot_credit.get_text(strip=True))
    else:
        total_credits = sum(v["occasions"] for v in volunteer_data)

    volunteer_data.append({"role": "Total Credits", "occasions": total_credits})

    result = {
        "source": "parkrun 2305995",
        "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "data": volunteer_data,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/parkrun.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Volunteer data extracted and saved to data/parkrun.json.")

if __name__ == "__main__":
    main()
