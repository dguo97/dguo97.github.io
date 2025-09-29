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
            await page.wait_for_selector("table#results", timeout=5000)
        except:
            return  # abort silently if table not found

        # Get all tables with id="results"
        tables = await page.query_selector_all("table#results")

        volunteer_data = None
        # Find the table whose header contains "Role" and "Occasions"
        for table in tables:
            header_html = await table.inner_html()
            if "Role" in header_html and "Occasions" in header_html:
                # This is the Volunteer Summary Table
                volunteer_data = await table.eval_on_selector_all(
                    "tbody tr",
                    """rows => rows.map(r => {
                        const cols = r.querySelectorAll("td");
                        return { role: cols[0].innerText.trim(), occasions: parseInt(cols[1].innerText.trim()) || 0 };
                    })"""
                )
                # Extract total credits
                total_credits_el = await table.query_selector("tfoot tr td:last-child")
                total_credits = int(await total_credits_el.inner_text()) if total_credits_el else sum(v['occasions'] for v in volunteer_data)
                volunteer_data.append({"role": "Total Credits", "occasions": total_credits})
                break

        if not volunteer_data:
            return  # abort silently if no correct table found

        # Save JSON only if data exists
        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": volunteer_data
        }

        os.makedirs("data", exist_ok=True)
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

asyncio.run(main())
