import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Go to the Parkrun profile page
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/", wait_until="networkidle")
        
        # Scroll down to trigger lazy loading if necessary
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3000)  # wait 3s for JS to render

        # Get page content
        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        container = soup.select_one("#volunteer-summary")
        table = container.find("table") if container else None

        if not table:
            raise ValueError("Volunteer summary table missing after HTML parsing")

        data = []

        # Extract rows
        for row in table.select("tbody tr"):
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            role = cols[0].text.strip()
            try:
                occasions = int(cols[1].text.strip())
            except ValueError:
                occasions = 0
            data.append({"role": role, "occasions": occasions})

        # Extract total credits directly if available
        tfoot_total = table.select_one("tfoot tr td:nth-child(2)")
        if tfoot_total:
            total_credits = int(tfoot_total.text.strip())
        else:
            total_credits = sum(item["occasions"] for item in data)

        data.append({"role": "Total Credits", "occasions": total_credits})

        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": data
        }

        # Ensure data folder exists
        os.makedirs("data", exist_ok=True)
        
        # Save to JSON
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

        print("✅ Parkrun volunteer data updated successfully")

# Run the scraper
asyncio.run(main())
