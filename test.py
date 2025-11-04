import time
import requests, random, pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor as Pool


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
# Using a random UA in user_agents each time
def ua(): return {"User-Agent": random.choice(user_agents)}

# URL details
BASE = "https://www.immovlan.be/en/real-estate"
PARAMS = {"transactiontypes": "for-sale,in-public-sale"}

# ---------- 1. grab one page ----------

def get_page(page):
    resp = requests.get(BASE, params={**PARAMS, "page": page},
                       headers=ua(), timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")          # lxml is faster
    links = []
    for card in soup.find_all("article", class_="list-view-item"):
        a = card.select_one("h2.card-title a")
        if a:
            url = a["href"]
            links.append(url)
            print(url)
    print(f"page {page} → {len(links)} links")
    return links

# Discover pages until page 50
MAX_SITE_PAGES = 50
page = 1
while page < MAX_SITE_PAGES:
    if not get_page(page):
        page -= 1
        break
    page += 1
print(f"total pages scraped: {page} (capped at {MAX_SITE_PAGES})")

# ---------- 3. fetch 2..last in parallel ----------
with Pool(max_workers=20) as pool:
    pages = pool.map(get_page, range(1, page + 1))

all_links = [url for page in pages for url in page]
print(f"Total links collected: {len(all_links)}")

pd.DataFrame({"url":all_links}).to_csv("immovlan_1000.csv", index=False)
# # ---- Iterating through the urls on a page ----
# # List page
# response = requests.get(BASE, params=PARAMS, headers=ua())
# response.raise_for_status()
# soup = BeautifulSoup(response.text, 'html.parser')
#
# listings = []
# page = 1
# while True:
#     print(f"--- scraping page {page} ---")
#     resp = requests.get(BASE, params={**PARAMS, "page": page}, headers=ua(), timeout=10)
#     resp.raise_for_status()
#     soup = BeautifulSoup(resp.text, "html.parser")
#
#     cards = soup.find_all("article", class_="list-view-item")
#     if not cards:                       # safety exit
#         break
#
#     for card in cards:
#         link = card.select_one("h2.card-title a")
#         if link:
#             url = link["href"]
#             listings.append({"url": url})
#             print(url)
#
#     # Stop when no "text" button / link
#     next_link = soup.select_one('a[rel="next"], a:-soup-contains("Next"), a[aria-label="Next"]')
#     if next_link is None:
#         break
#
#     page += 1
#     time.sleep(random.uniform(0.8, 1.5))
# print(f"{len(listings)} properties found on {page} pages.")