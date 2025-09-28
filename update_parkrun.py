from bs4 import BeautifulSoup

# Load your HTML file
with open("parkrun.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Find the Volunteer Summary section
vol_summary_header = soup.find("h3", string="Volunteer Summary")
if vol_summary_header:
    table = vol_summary_header.find_next("table")  # the table right after the header
    volunteer_summary = []

    # Extract table rows
    for row in table.find_all("tr")[1:]:  # skip header row
        cols = row.find_all("td")
        role = cols[0].text.strip()
        occasions = cols[1].text.strip()
        volunteer_summary.append((role, occasions))

    # Print results
    print("Volunteer Summary:")
    for role, occasions in volunteer_summary:
        print(f"{role}: {occasions}")
else:
    print("Volunteer Summary not found.")
