import os
import re
os.environ['no_proxy'] = '*'
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://digimoviez48.top/movies"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def get_session():
    session = requests.Session()
    session.proxies = {}
    session.trust_env = False
    return session

def choose_image_url(img_tag):
    srcset = img_tag.get("srcset")
    if srcset:
        candidates = []
        for part in srcset.split(","):
            part = part.strip()
            if not part:
                continue
            parts = part.split()
            if len(parts) >= 2:
                url = parts[0]
                size = parts[-1]
                width_match = re.search(r"(\d+)w$", size)
                width = int(width_match.group(1)) if width_match else 0
                candidates.append((width, url))
        if candidates:
            return sorted(candidates, key=lambda x: x[0])[-1][1]
    return img_tag.get("src")

def extract_posters_from_page(page_num, session):
    if page_num == 1:
        url = f"{BASE_URL}/"
    else:
        url = f"{BASE_URL}/page/{page_num}/"

    print(f"Fetching page {page_num}: {url}")
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    posters = []

    for item in soup.select("div.item_small_loop"):
        img = item.select_one("img")
        if img is None:
            continue

        image_url = choose_image_url(img)
        if not image_url:
            continue

        title = img.get("alt") or img.get("title") or "unknown"

        if image_url.startswith("//"):
            image_url = "https:" + image_url

        posters.append({
            "page": page_num,
            "title": title,
            "image_url": image_url,
        })

    return posters

session = get_session()

for page_num in [185, 186, 187]:
    posters = extract_posters_from_page(page_num, session)
    print(f"Page {page_num}: Found {len(posters)} posters")
    if posters:
        for i, p in enumerate(posters[:2]):
            print(f"  {i+1}. {p['title'][:50]} - {p['image_url'][:60]}")
    print()
