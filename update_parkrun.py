import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/", wait_until="networkidle")
        
        # Extract volunteer data from the table with id="results"
        volunteer_data = await page.eval_on_selector_all(
            "#results tbody tr",
            """rows => rows.map(r => {
                const cols = r.querySelectorAll("td");
                const role = cols[0].innerText.trim();
                const occasions = parseInt(cols[1].innerText.trim()) || 0;
                return { role, occasions };
            })"""
        )

        if not volunteer_data:
            raise ValueError("Could not extract volunteer data")

        # Extract total credits from the table footer
        total_credits_el = await page.query_selector("#results tfoot tr td:last-child")
        total_credits = int(await total_credits_el.inner_text()) if total_credits_el else sum(v['occasions'] for v in volunteer_data)
        
        volunteer_data.append({"role": "Total Credits", "occasions": total_credits})

        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": volunteer_data
        }

        # Ensure the data directory exists
        os.makedirs("data", exist_ok=True)

        # Write JSON data
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

        print("✅ Parkrun volunteer data updated successfully")

# Run the async main function
asyncio.run(main())
