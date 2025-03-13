import requests
from bs4 import BeautifulSoup

URL = "https://www.prospektmaschine.de/hypermarkte/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(URL, headers=HEADERS)

# Save the raw HTML to file
with open("debug.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML saved to debug.html")
