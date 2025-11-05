# from http.client import responses

# from selenium import webdriver  # to start the browser
# from selenium.webdriver.common.by import By  # how to find elements (by XPATH, by ID..)
# from selenium.webdriver.support.ui import WebDriverWait  # waiting for elements to be clickable + EC
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException  # in case an element is not found in time
# import time  # optional delay to avoid getting banned, wait for popups


import requests, pandas as pd, re, random, csv
from bs4 import BeautifulSoup

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
headers = {'User-Agent': random.choice(user_agents)}


# Read the list
input_csv = "property_urls.csv"
with open(input_csv, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

# Scrape every url
all_specs = []
for url in urls:
    soup = BeautifulSoup(requests.get(url,headers=headers).text, "html.parser")
    specs = {}

    for li in soup.select("ul li"):
        txt = li.get_text(strip=True)
        m = re.match(r"^(.+?):\s*(.+)$", txt)
        if m:
            specs[m.group(1)] = m.group(2)

    for h4 in soup.select("h4"):
        p = h4.find_next("p")
        if p:
            specs[h4.get_text(strip=True)] = p.get_text(strip=True)
    # -----------------------------------------------------

    specs["URL"] = url


    all_specs.append(specs)

    print(url)
    for k, v in specs.items():
        if k != "URL":
            print(f"{k}: {v}")


# One data-frame with every property
df = pd.DataFrame(all_specs)
df.to_csv("immovlan_final_file.csv", index=False)
