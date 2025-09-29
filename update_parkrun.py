import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/")

        # Wait for at least one results table
        try:
            await page.wait_for_selector("table#results", timeout=15000)
        except:
            print("No table#results found")
            return

        tables = await page.query_selector_all("table#results")
        print(f"Found {len(tables)} tables with id='results'.")

        volunteer_data = None
        for idx, table in enumerate(tables):
            # Find thead th cells
            thead = await table.query_selector("thead")
            if not thead:
                continue
            headers = await thead.query_selector_all("th")
            headers_text = [((await h.inner_text()).strip()) for h in headers]
            print(f"Table {idx} headers: {headers_text}")

            # Look for "Role" and "Occasions"
            if headers_text == ["Role", "Occasions"]:
                rows = await table.query_selector_all("tbody tr")
                volunteer_data = []
                for row in rows:
                    cols = await row.query_selector_all("td")
                    if len(cols) >= 2:
                        role = (await cols[0].inner_text()).strip()
                        occasions = int((await cols[1].inner_text()).strip())
                        volunteer_data.append({"role": role, "occasions": occasions})
                # Total credits from tfoot
                tfoot = await table.query_selector("tfoot")
                if tfoot:
                    total_cells = await tfoot.query_selector_all("tr td")
                    if len(total_cells) >= 2:
                        total_credits = int((await total_cells[1].inner_text()).strip())
                        volunteer_data.append({"role": "Total Credits", "occasions": total_credits})
                break

        if not volunteer_data:
            print("No volunteer summary table found.")
            return

        # Save JSON only if data exists
        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": volunteer_data
        }

        os.makedirs("data", exist_ok=True)
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Volunteer data saved to data/parkrun.json")

asyncio.run(main())
