#!/usr/bin/env python
"""Ultimate test - no proxy, no SOCKS, pure connection"""

import os
import sys

# Remove ALL proxy environment variables
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    if var in os.environ:
        del os.environ[var]

os.environ['no_proxy'] = '*'

import requests

print("Testing direct connection...")
print("-" * 60)

session = requests.Session()
session.proxies = {}
session.trust_env = False
session.verify = False

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

url = 'https://digimoviez.com/movies/'

try:
    print(f"URL: {url}")
    print(f"Proxies: {session.proxies}")
    print(f"Trust env: {session.trust_env}")
    print(f"Verify SSL: {session.verify}")
    print()
    
    resp = session.get(url, headers=headers, timeout=10)
    print(f"✅ Status: {resp.status_code}")
    print(f"✅ Content length: {len(resp.content)} bytes")
    print(f"✅ Connection successful!")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    sys.exit(1)
