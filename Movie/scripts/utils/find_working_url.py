#!/usr/bin/env python
"""Test various URLs to find working domain"""

import os
import requests

# Remove proxies
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    if var in os.environ:
        del os.environ[var]

os.environ['no_proxy'] = '*'

session = requests.Session()
session.proxies = {}
session.trust_env = False
session.verify = False

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test multiple URLs
urls = [
    'https://digimoviez.com/movies/',
    'https://digimoviez.com/',
    'http://digimoviez.com/movies/',
    'http://digimoviez.com/',
    'https://digimoviez47.top/movies/',
    'https://digimoviez48.top/movies/',
    'https://digimoviez.top/movies/',
    'https://www.digimoviez.com/movies/',
]

print("Testing URLs...")
print("=" * 70)

for url in urls:
    try:
        print(f"\n🔍 Testing: {url}")
        resp = session.get(url, headers=headers, timeout=5)
        print(f"   ✅ Status: {resp.status_code}")
        print(f"   ✅ Size: {len(resp.content)} bytes")
        print(f"   ✅ SUCCESS!")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection refused")
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout")
    except Exception as e:
        print(f"   ❌ {type(e).__name__}: {str(e)[:50]}")

print("\n" + "=" * 70)
print("Check which URL works above! 👆")
