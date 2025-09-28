import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Go to the Parkrun page
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/", wait_until="networkidle")
        
        # Wait up to 60s for the table to appear
        try:
            await page.wait_for_selector("table#volunteer-history", timeout=60000)
        except:
            await browser.close()
            raise ValueError("Volunteer history table not found on the page")
        
        # Get the page HTML after JS rendering
        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        table = soup.select_one("table#volunteer-history")
        if not table:
            raise ValueError("Volunteer history table missing after HTML parsing")

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

        # Save to JSON
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

        print("✅ Parkrun volunteer data updated successfully")

asyncio.run(main())
