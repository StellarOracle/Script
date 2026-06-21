#!/usr/bin/env python
"""Extract poster image URLs from digimoviez.com pages 1..837.
Saves unique URLs to poster_urls.txt and poster_urls.csv (with title and page).
"""
import re
import time
import csv
import os
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as exc:
    raise SystemExit("Missing dependency: pip install requests beautifulsoup4")

BASE_URL = "https://digimoviez48.top/movies"
OUT_TXT = "poster_urls.txt"
OUT_CSV = "poster_urls.csv"
START_PAGE = 1
END_PAGE = 837
DELAY = 0.3
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

size_re = re.compile(r"-\d+x\d+(?=\.[a-zA-Z]{2,4}$)")


def choose_best_from_srcset(img_tag):
    srcset = img_tag.get("srcset")
    if srcset:
        candidates = []
        for part in srcset.split(","):
            part = part.strip()
            if not part:
                continue
            pieces = part.split()
            url = pieces[0]
            if len(pieces) > 1 and pieces[-1].endswith('w'):
                try:
                    width = int(pieces[-1][:-1])
                except Exception:
                    width = 0
            else:
                width = 0
            candidates.append((width, url))
        if candidates:
            return sorted(candidates, key=lambda x: x[0])[-1][1]
    # fallback
    return img_tag.get("src")


def to_original(url):
    # Replace patterns like -200x300 before file extension
    return size_re.sub("", url)


def extract_from_page(page):
    if page == 1:
        url = BASE_URL + "/"
    else:
        url = f"{BASE_URL}/page/{page}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed page {page}: {e}")
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for item in soup.select('div.item_small_loop'):
        img = item.select_one('img')
        if not img:
            continue
        best = choose_best_from_srcset(img)
        if not best:
            continue
        if best.startswith('//'):
            best = 'https:' + best
        orig = to_original(best)
        title = img.get('alt') or img.get('title') or ''
        results.append((orig, title.strip()))
    return results


def main(start_page=START_PAGE, end_page=END_PAGE):
    import argparse
    parser = argparse.ArgumentParser(description='Extract poster URLs')
    parser.add_argument('--start', type=int, default=start_page, help='start page')
    parser.add_argument('--end', type=int, default=end_page, help='end page')
    args = parser.parse_args()

    seen = set()
    rows = []
    os.makedirs('.', exist_ok=True)
    for page in range(args.start, args.end + 1):
        print(f"Scanning page {page}...")
        items = extract_from_page(page)
        if not items:
            print(f"  No items on page {page} (or failed).")
        for url, title in items:
            if url in seen:
                continue
            seen.add(url)
            rows.append({'page': page, 'title': title, 'url': url})
        if page % 50 == 0:
            print(f"  Scanned page {page} - collected {len(seen)} unique URLs so far")
        time.sleep(DELAY)

    # write txt
    with open(OUT_TXT, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(r['url'] + '\n')
    # write csv
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['page','title','url'])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} unique URLs to {OUT_TXT} and {OUT_CSV}")


if __name__ == '__main__':
    main()
