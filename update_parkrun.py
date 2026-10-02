import json
import os
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://www.parkrun.org.uk/parkrunner/2305995/"
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")

def main():
    if SCRAPER_API_KEY:
        print("Using ScraperAPI proxy (bypassing cache)...")
        payload = {
            "api_key": SCRAPER_API_KEY,
            "url": TARGET_URL,
            "render": "false",
            "cache": "false",  # Forces ScraperAPI to fetch live HTML
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

    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the volunteer table (try ID heading first, fallback to table headers)
    heading = soup.find("h3", id="volunteer-summary")
    volunteer_table = None

    if heading and heading.parent:
        volunteer_table = heading.parent.find("table")

    if not volunteer_table:
        # Fallback: Find table containing "Volunteer Summary" or role columns
        for table in soup.find_all("table"):
            if "Volunteer Summary" in table.get_text() or "Role" in table.get_text():
                volunteer_table = table
                break

    if not volunteer_table:
        print("Error: Volunteer Summary table could not be found in the response HTML.")
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
        print("Error: Table found but zero data rows parsed.")
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
