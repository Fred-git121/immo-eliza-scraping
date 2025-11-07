import time, random, pandas as pd, requests
from bs4 import BeautifulSoup

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
# Using a random UA in user_agents each time
def ua(): return {"User-Agent": random.choice(user_agents)}

BASE = "https://www.immovlan.be/en/real-estate"

# --------------- 1. PARAMS -----------------------------

SALE_REGIONS = {
    "Brussels": {"transactiontypes": "for-sale", "provinces": "brussels"},
    "Hainaut": {"transactiontypes": "for-sale", "provinces": "hainaut"},
    "East Flanders": {"transactiontypes": "for-sale", "provinces": "east-flanders"},
    "Luxembourg": {"transactiontypes": "for-sale", "provinces": "luxembourg"},
    "Antwerp": {"transactiontypes": "for-sale", "provinces": "antwerp"},
    "Brabant Wallon": {"transactiontypes": "for-sale", "provinces": "brabant-wallon"},
    "Liège": {"transactiontypes": "for-sale", "provinces": "liege"},
    "Namur": {"transactiontypes": "for-sale", "provinces": "namur"},
    "West Flanders": {"transactiontypes": "for-sale", "provinces": "west-flanders"},
    "Vlaams Brabant": {"transactiontypes": "for-sale", "provinces": "vlaams-brabant"},
    "Limburg": {"transactiontypes": "for-sale", "provinces": "limburg"}
}

# --------------- 2. GRAB ONE PAGE --------------------------
def get_page(page, params_dict, label):
    params = {**params_dict, "page": page}
    r = requests.get(BASE, params=params, headers=ua(), timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    links = [(a["href"], label) for card in soup.select("article.list-view-item")
             for a in [card.select_one("h2.card-title a")] if a]
    print(f"{label} page {page} → {len(links)} links")
    return links

# --------------- 3. SCRAPER -------------------------
MAX_SITE_PAGES = 50

def scrape_category(params_dict, label):
    # Scrape every page for one category; returns list[(url,label)]
    all_links = []
    for p in range(1, MAX_SITE_PAGES + 1):
        batch = get_page(p, params_dict, label)
        if not batch:          # empty page → we reached the end
            break
        all_links.extend(batch)
    print(f"{label} pages scraped: {len(all_links)} links")
    return all_links

# --------------- 4. RUN EVERYTHING (category-by-category) -------
all_links = []

# 4a. sale sub-categories in the required order
for label, params in SALE_REGIONS.items():          # dict keeps insertion order in py≥3.7
    print(f"\n===== SCRAPING {label.upper()} =====")
    all_links.extend(scrape_category(params, label))

# --------------- 5. SAVE -----------------------------------
df = pd.DataFrame(all_links, columns=["url", "province"]).drop_duplicates(subset="url")
df.to_csv("immovlan_sale.csv", index=False)
print(f"\nTotal unique links collected: {len(df)}")


# scraping from one url

import requests, pandas as pd, re, random
from bs4 import BeautifulSoup

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
headers = {'User-Agent': random.choice(user_agents)}

url = "https://immovlan.be/en/detail/investment-property/for-sale/7060/soignies/rbu62401"
soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

specs = {}

# <ul><li><strong>Label:</strong> Value</li>
for li in soup.select("ul li"):
    txt = li.get_text(strip=True)
    m = re.match(r"^(.+?):\s*(.+)$", txt)  # "Label: Value"
    if m:
        specs[m.group(1)] = m.group(2)

# Every <h4><p> pair on the page
for h4 in soup.select("h4"):
    p = h4.find_next("p")
    if p:
        label = h4.get_text(strip=True)
        val = p.get_text(strip=True)
        specs[label] = val

# ---- Description ----
desc_tag = soup.select_one("div:has(> h2:-soup-contains('Description')) + div")
if desc_tag:
    specs["Description"] = desc_tag.get_text(" ", strip=True)

# ---- View ----
df = pd.DataFrame([specs])
print(df.T)    # transpose for quick read
df.to_csv("immovlan_one_page.csv", index=False)

# url = "https://immovlan.be/en/detail/investment-property/for-sale/7060/soignies/rbu62401"
# soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
#
# # 1. Every H3 text

# print("H3 texts:")
# for h in soup.select("h3"):
#     print("-", h.get_text(strip=True))







