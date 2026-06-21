import os
os.environ['no_proxy'] = '*'
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.proxies = {}
session.trust_env = False
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://digimoviez48.top/movies/page/185/'
resp = session.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

items = soup.select('div.item_small_loop')
print(f'Found {len(items)} items\n')

for i, item in enumerate(items[:5]):
    img = item.select_one('img')
    print(f'Item {i}:')
    if img:
        print(f'  img tag found')
        print(f'  src: {img.get("src")}')
        print(f'  srcset: {str(img.get("srcset"))[:100] if img.get("srcset") else None}')
        print(f'  alt: {img.get("alt")}')
        print(f'  title: {img.get("title")}')
    else:
        print(f'  NO img tag!')
        print(f'  Item HTML: {str(item)[:300]}')
    print()
