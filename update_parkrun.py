import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/")
        await page.wait_for_selector("table#volunteer-history")  # wait until table loads

        content = await page.content()
        await browser.close()

        # Parse the HTML
        soup = BeautifulSoup(content, "html.parser")
        table = soup.select_one("table#volunteer-history")
        if not table:
            raise ValueError("Volunteer history table not found")

        data = []
        total_credits = 0

        for row in table.select("tbody tr"):
            cols = row.find_all("td")
            role = cols[0].text.strip()
            occasions_text = cols[1].text.strip()
            try:
                occasions = int(occasions_text)
            except ValueError:
                occasions = 0
            data.append({"role": role, "occasions": occasions})
            total_credits += occasions

        # Add total row
        data.append({"role": "Total Credits", "occasions": total_credits})

        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": data
        }

        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

asyncio.run(main())
