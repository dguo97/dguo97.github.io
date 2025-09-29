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

        # Wait up to 10 seconds for ANY #results table to appear
        try:
            await page.wait_for_selector("table#results", timeout=10000)
        except:
            print("No table#results found (timeout).")
            return

        # Find all tables with id="results"
        tables = await page.query_selector_all("table#results")
        volunteer_table = None

        # Look for table whose header contains "Role" and "Occasions"
        for table in tables:
            header = await table.inner_text()
            if "Role" in header and "Occasions" in header:
                volunteer_table = table
                break

        if not volunteer_table:
            print("Volunteer Summary table not found.")
            return

        # Extract volunteer data rows
        volunteer_data = await volunteer_table.eval_on_selector_all(
            "tbody tr",
            """rows => rows.map(r => {
                const cols = r.querySelectorAll("td");
                return { role: cols[0].innerText.trim(), occasions: parseInt(cols[1].innerText.trim()) || 0 };
            })"""
        )

        if not volunteer_data:
            print("No volunteer data rows found.")
            return

        # Extract total credits from tfoot if present, else sum
        total_credits_el = await volunteer_table.query_selector("tfoot tr td:last-child")
        if total_credits_el:
            total_credits = int((await total_credits_el.inner_text()).strip())
        else:
            total_credits = sum(v['occasions'] for v in volunteer_data)
        volunteer_data.append({"role": "Total Credits", "occasions": total_credits})

        # Save JSON only if data exists
        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": volunteer_data
        }

        os.makedirs("data", exist_ok=True)
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Volunteer data extracted and saved to data/parkrun.json.")

asyncio.run(main())
