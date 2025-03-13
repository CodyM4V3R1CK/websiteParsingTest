import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Constants
URL = "https://www.prospektmaschine.de/hypermarkte/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # Fake browser identity to avoid bot detection
}

# Function to parse date ranges with different formats
def parse_date_range(text):
    try:
        text = text.strip()
        if "-" in text:  # Check if text contains a date range
            parts = text.split("-")
            valid_from = datetime.strptime(parts[0].strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
            valid_to = datetime.strptime(parts[1].strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
        elif "von" in text:  # Check if text contains a single date (starting from)
            date_str = text.split("von")[-1].strip().split()[-1]  # Extract the last part of "von" string
            valid_from = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            valid_to = None  # Open-ended date range
        else:
            valid_from = valid_to = None  # Default to None if parsing fails
    except Exception:  # Catch parsing errors and set dates to None
        valid_from = valid_to = None
    return valid_from, valid_to

# Main scraping logic
def fetch_leaflets():
    response = requests.get(URL, headers=HEADERS)
    if not response.ok:
        print("Failed to fetch the page. Check the URL or headers!")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    grid = soup.find("div", class_="letaky-grid")  # Locate the grid containing brochures

    if not grid:
        print("Grid containing brochures not found on the page!")
        return []

    # Process cards from the grid
    leaflets = []
    cards = grid.find_all("div", class_="brochure-thumb col-xs-6 col-sm-3")

    for card in cards:
        try:
            # Extract image thumbnail
            img_tag = card.find("img")
            thumbnail = img_tag.get("data-src") or img_tag.get("src")

            # Extract text information from brochure description
            desc = card.find("div", class_="letak-description")
            info_lines = desc.find_all("p", class_="grid-item-content")

            # Extract shop name and date text
            shop_name = info_lines[0].get_text(strip=True) if len(info_lines) > 0 else "Unknown"
            date_text = info_lines[1].find("small").get_text(strip=True) if len(info_lines) > 1 else ""

            # Parse date range
            valid_from, valid_to = parse_date_range(date_text)

            # Append leaflet data to the list
            leaflets.append({
                "shop_name": shop_name,
                "thumbnail": thumbnail,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "parsed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            print(f"Error parsing card: {e}")

    return leaflets

# Save data to a JSON file
def save_to_json(data, filename="leaflets.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(data)} leaflets to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")


# Main execution
if __name__ == "__main__":
    print("Fetching leaflets...")
    leaflets = fetch_leaflets()  # Fetch leaflets data

    if leaflets:
        save_to_json(leaflets)  # Save to JSON file
    else:
        print("No leaflets found or data could not be parsed!")
