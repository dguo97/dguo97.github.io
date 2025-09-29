import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import os

async def main():
    async with async_playwright() as p:
        # Always use headless=True for CI/server environments
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/")

        # Take a screenshot for debugging, even on failure
        try:
            # Wait for the Volunteer Summary heading
            heading = await page.wait_for_selector("h3#volunteer-summary", timeout=15000)
        except:
            await page.screenshot(path="debug-volunteer-summary-not-found.png", full_page=True)
            print("Volunteer Summary heading not found.")
            return

        # Find the parent div of the heading and then the table inside
        parent = await heading.evaluate_handle('node => node.parentElement')
        volunteer_table = await parent.query_selector('table')
        if not volunteer_table:
            await page.screenshot(path="debug-volunteer-table-not-found.png", full_page=True)
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
            await page.screenshot(path="debug-no-volunteer-rows.png", full_page=True)
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
