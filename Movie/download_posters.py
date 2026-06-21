#!/usr/bin/env python
"""Download movie posters from digimoviez.com pages 1..837.

Usage:
    python download_posters.py --start-page 199
    python download_posters.py --start-page 199 --end-page 837 --append

Requirements:
    pip install requests beautifulsoup4
"""

import argparse
import csv
import os
import re
import time
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: install with `pip install requests beautifulsoup4`"
    ) from exc

# Disable SOCKS proxy support
import urllib3
urllib3.disable_warnings()
os.environ['no_proxy'] = '*'

BASE_URL = "https://digimoviez48.top/movies"
OUTPUT_DIR = "posters"
CSV_FILE = "posters.csv"
START_PAGE = 184
END_PAGE = 837
DELAY_SECONDS = 0.8
MAX_RETRIES = 3
RETRY_BACKOFF = 3
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    # Removed Accept-Encoding as it causes server to return empty content for some pages
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def get_session():
    """Create a requests session without proxy."""
    # Disable proxy environment variables
    os.environ['no_proxy'] = '*'
    for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        if var in os.environ:
            del os.environ[var]
    
    session = requests.Session()
    session.proxies = {}
    session.trust_env = False
    return session


def safe_filename(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]+", "-", text)
    text = text.strip().replace(" ", "_")
    return text[:180]


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


def download_image(image_url, filename, output_dir, session):
    """Download image if it doesn't already exist.
    
    Args:
        image_url: URL of the image to download
        filename: Name to save the file as
        output_dir: Directory to save the file in
        session: requests.Session object
    
    Returns:
        tuple: (filepath, already_existed)
    """
    path = os.path.join(output_dir, filename)
    if os.path.exists(path):
        print(f"  already exists: {filename}")
        return path, True

    try:
        response = session.get(image_url, headers=HEADERS, stream=True, timeout=30)
        response.raise_for_status()
        with open(path, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)
        return path, False
    except Exception as exc:
        # If download failed, remove the partial file
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        raise exc


def url_to_filename(image_url, title, page_num, index):
    parsed = urlparse(image_url)
    base_name = os.path.basename(parsed.path)
    if not base_name:
        base_name = f"poster_{page_num}_{index}.jpg"
    else:
        base_name = safe_filename(base_name)

    title_part = safe_filename(title)
    return f"{page_num:03d}_{index:03d}_{title_part}_{base_name}"


def parse_args():
    parser = argparse.ArgumentParser(description="Download movie posters from digimoviez.com pages.")
    parser.add_argument("--start-page", type=int, default=START_PAGE, help="First page to download")
    parser.add_argument("--end-page", type=int, default=END_PAGE, help="Last page to download")
    parser.add_argument("--delay", type=float, default=DELAY_SECONDS, help="Delay between pages in seconds")
    parser.add_argument("--retries", type=int, default=MAX_RETRIES, help="Number of retries for page download failures")
    parser.add_argument("--backoff", type=float, default=RETRY_BACKOFF, help="Base backoff multiplier for retry delays")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Folder to save downloaded posters")
    parser.add_argument("--csv", default=CSV_FILE, help="CSV file for metadata")
    parser.add_argument("--append", action="store_true", help="Load existing CSV and append new rows")
    return parser.parse_args()


def load_existing_rows(csv_file):
    rows = []
    if not os.path.exists(csv_file):
        return rows

    with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    rows = load_existing_rows(args.csv) if args.append else []
    if args.append and rows:
        print(f"Loaded {len(rows)} existing rows from {args.csv}")

    session = get_session()

    for page_num in range(args.start_page, args.end_page + 1):
        posters = None
        for attempt in range(1, args.retries + 1):
            try:
                posters = extract_posters_from_page(page_num, session)
                break
            except Exception as exc:
                print(f"Error fetching page {page_num} (attempt {attempt}/{args.retries}): {exc}")
                if attempt < args.retries:
                    wait_time = args.backoff * attempt
                    print(f"  retrying after {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  skipping page {page_num} after {args.retries} failed attempts.")

        if posters is None:
            continue

        if not posters:
            print(f"No posters found on page {page_num}, skipping.")
            time.sleep(args.delay)
            continue

        new_count = 0
        skip_count = 0
        for idx, poster in enumerate(posters, start=1):
            image_url = poster["image_url"]
            filename = url_to_filename(image_url, poster["title"], page_num, idx)
            try:
                filepath, already_existed = download_image(image_url, filename, args.output_dir, session)
                if already_existed:
                    skip_count += 1
                else:
                    new_count += 1
            except Exception as exc:
                print(f"  failed to download {image_url}: {exc}")
                continue

            # Add to rows only if it's new or if we're starting fresh
            if not already_existed or not args.append:
                rows.append(
                    {
                        "page": page_num,
                        "title": poster["title"],
                        "image_url": image_url,
                        "filename": filename,
                    }
                )

        print(f"Downloaded {new_count} new posters, skipped {skip_count} existing from page {page_num}")
        time.sleep(args.delay)

    if rows:
        with open(args.csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["page", "title", "image_url", "filename"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved metadata to {args.csv}")

    print("Done.")


if __name__ == "__main__":
    main()
