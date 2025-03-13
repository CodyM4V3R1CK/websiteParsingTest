import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

URL = "https://www.prospektmaschine.de/hypermarkte/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"   # Fake browser identity = no bot
}

response = requests.get(URL, headers=HEADERS)

leaflets = []

# Save the raw HTML to file
with open("debug.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML saved to debug.html")

with open("debug.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

def parse_date_range(text):
    try:
        text = text.strip()
        if "-" in text:
            parts = text.split("-")
            valid_from = datetime.strptime(parts[0].strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
            valid_to = datetime.strptime(parts[1].strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
        elif "von" in text:
            date_str = text.split("von")[-1].strip().split()[-1]  # gets last part like "15.11.2022"
            valid_from = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            valid_to = None
        else:
            valid_from = valid_to = None
    except Exception:
        valid_from = valid_to = None
    return valid_from, valid_to

# Find the flier grid
grid = soup.find("div", class_="letaky-grid")
if grid:
    cards = grid.find_all("div", class_="brochure-thumb col-xs-6 col-sm-3")

    for card in cards:
        try:
            # Extract image thumbnail
            img_tag = card.find("img")
            thumbnail = img_tag.get("data-src") or img_tag.get("src")

            # Extract text info from letak-description
            desc = card.find("div", class_="letak-description")
            info_lines = desc.find_all("p", class_="grid-item-content")

            shop_name = info_lines[0].get_text(strip=True) if len(info_lines) > 0 else "Unknown"
            date_text = info_lines[1].find("small").get_text(strip=True) if len(info_lines) > 1 else ""

            valid_from, valid_to = parse_date_range(date_text)

            leaflets.append({
                "title": "Prospekt",
                "thumbnail": thumbnail,
                "shop_name": shop_name,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "parsed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            print(f"Error parsing card: {e}")

# Save to JSON
with open("leaflets.json", "w", encoding="utf-8") as f:
    json.dump(leaflets, f, indent=4, ensure_ascii=False)

print(f"Saved {len(leaflets)} leaflets to leaflets.json")