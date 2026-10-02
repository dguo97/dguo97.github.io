import json
import os
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://www.parkrun.org.uk/parkrunner/2305995/"
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")

def main():
    # Route through ScraperAPI if key exists; otherwise fetch directly
    if SCRAPER_API_KEY:
        print("Using ScraperAPI proxy...")
        payload = {
            "api_key": SCRAPER_API_KEY,
            "url": TARGET_URL,
            "render": "false",  # Simple HTML request (1 credit per call)
        }
        try:
            response = requests.get("https://api.scraperapi.com/", params=payload, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"ScraperAPI request failed: {e}")
            return
    else:
        print("Fetching target URL directly...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Accept-Language": "en-GB,en;q=0.9",
        }
        try:
            response = requests.get(TARGET_URL, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Direct request failed: {e}")
            return

    if "Let's confirm you are human" in response.text:
        print("Cloudflare verification challenge encountered.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    heading = soup.find("h3", id="volunteer-summary")
    if not heading:
        print("Volunteer Summary heading not found.")
        return

    parent = heading.parent
    volunteer_table = parent.find("table") if parent else None
    if not volunteer_table:
        print("Volunteer Summary table not found.")
        return

    volunteer_data = []
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

    tfoot_credit = volunteer_table.select_one("tfoot tr td:last-child")
    if tfoot_credit and tfoot_credit.get_text(strip=True).isdigit():
        total_credits = int(tfoot_credit.get_text(strip=True))
    else:
        total_credits = sum(v["occasions"] for v in volunteer_data)

    volunteer_data.append({"role": "Total Credits", "occasions": total_credits})

    result = {
        "source": "parkrun 2305995",
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "data": volunteer_data,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/parkrun.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Volunteer data extracted and saved to data/parkrun.json.")

if __name__ == "__main__":
    main()
