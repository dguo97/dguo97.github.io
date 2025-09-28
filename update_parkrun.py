import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import os

async def main():
    os.makedirs("data", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/", wait_until="networkidle")
        
        # Extract volunteer summary table rows
        volunteer_data = await page.eval_on_selector_all(
            "#volunteer-summary table tr",
            """rows => rows.slice(1).map(r => {
                const cells = r.querySelectorAll('td');
                const role = cells[0]?.innerText.trim() || '';
                const occasions = parseInt(cells[1]?.innerText.replace(/,/g, '').trim()) || 0;
                return { role, occasions };
            })"""
        )

        if not volunteer_data:
            raise ValueError("Could not extract volunteer data")

        total_credits = sum(v['occasions'] for v in volunteer_data)
        volunteer_data.append({"role": "Total Credits", "occasions": total_credits})

        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": volunteer_data
        }

        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

        print("✅ Parkrun volunteer data updated successfully")

asyncio.run(main())
