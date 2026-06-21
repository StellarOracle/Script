import os
os.environ['no_proxy'] = '*'

import requests
from bs4 import BeautifulSoup

# Create session without proxy
session = requests.Session()
session.proxies = {}
session.trust_env = False

url='https://digimoviez48.top/movies/'
resp = session.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
print('status', resp.status_code)
soup = BeautifulSoup(resp.text, 'html.parser')
print('title', soup.title.string if soup.title else 'no title')
imgs = soup.select('article img, .post img, img')
print('img count', len(imgs))
print('first imgs')
for i, img in enumerate(imgs[:20]):
    print(i, img.get('src'), img.get('alt'))
