import os
import re
os.environ['no_proxy'] = '*'
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.proxies = {}
session.trust_env = False
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

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

url = 'https://digimoviez48.top/movies/page/185/'
resp = session.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

items = soup.select('div.item_small_loop')
print(f'Found {len(items)} items\n')

for i, item in enumerate(items[:3]):
    img = item.select_one('img')
    print(f'Item {i}:')
    
    image_url = choose_image_url(img)
    print(f'  choose_image_url result: {image_url}')
    
    if not image_url:
        print(f'  IMAGE_URL IS EMPTY/NONE - SKIPPED!')
    else:
        print(f'  OK - Would download')
    
    print()
