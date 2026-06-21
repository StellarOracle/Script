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

def extract_posters_from_page_debug(page_num, session):
    if page_num == 1:
        url = f"{BASE_URL}/"
    else:
        url = f"{BASE_URL}/page/{page_num}/"

    print(f"Fetching page {page_num}: {url}")
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    posters = []
    
    items = soup.select("div.item_small_loop")
    print(f"  Found {len(items)} div.item_small_loop elements")

    for idx, item in enumerate(items[:3]):
        print(f"\n  Item {idx}:")
        img = item.select_one("img")
        
        if img is None:
            print(f"    SKIP: No img tag")
            continue
        
        print(f"    img tag found")
        
        image_url = choose_image_url(img)
        print(f"    image_url = {image_url}")
        
        if not image_url:
            print(f"    SKIP: image_url is empty")
            continue
        
        print(f"    image_url OK")

        title = img.get("alt") or img.get("title") or "unknown"
        print(f"    title = {title[:40]}")

        if image_url.startswith("//"):
            image_url = "https:" + image_url
            print(f"    Fixed protocol-relative URL")

        posters.append({
            "page": page_num,
            "title": title,
            "image_url": image_url,
        })
        print(f"    ADDED to posters")

    return posters

session = get_session()
posters = extract_posters_from_page_debug(185, session)
print(f"\nTotal posters: {len(posters)}")
