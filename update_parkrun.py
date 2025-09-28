import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Go to the Parkrun profile page
        await page.goto("https://www.parkrun.org.uk/parkrunner/2305995/", wait_until="networkidle")
        
        # Wait for the volunteer summary table to appear
        try:
            await page.wait_for_selector("#volunteer-summary table", timeout=10000)  # 10s timeout
        except:
            raise ValueError("Volunteer summary table did not appear in time")
        
        # Extract table rows directly
        rows = await page.eval_on_selector_all(
            "#volunteer-summary table tbody tr",
            """rows => rows.map(row => {
                const cells = row.querySelectorAll('td');
                return {
                    role: cells[0]?.innerText.trim() || '',
                    occasions: parseInt(cells[1]?.innerText.trim() || '0')
                }
            })"""
        )

        # Calculate total credits
        total_credits = sum(row['occasions'] for row in rows)
        rows.append({"role": "Total Credits", "occasions": total_credits})

        # Prepare JSON
        result = {
            "source": "parkrun 2305995",
            "lastUpdated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "data": rows
        }

        # Save to JSON
        with open("data/parkrun.json", "w") as f:
            json.dump(result, f, indent=2)

        print("✅ Parkrun volunteer data updated successfully")

asyncio.run(main())
