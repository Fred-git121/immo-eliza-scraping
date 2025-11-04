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