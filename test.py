import requests, pandas as pd, re, random, csv
from bs4 import BeautifulSoup

def get_random_headers():
    user_agents =[
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ]
    return {"User-Agent": random.choice(user_agents)}
headers = get_random_headers()

# The columns that will be kept in the final file
KEEP = [
    "url",
    "Property ID",
    "Price",
    "State of the property",
    "Availability",
    "Number of bedrooms",
    "Livable surface",
    "Furnished",
    "Surface of living room",
    "Attic",
    "Garage",
    "Number of garages",
    "Kitchen equipment",
    "Kitchen type",
    "Number of bathrooms",
    "Number of showers",
    "Number of toilets",
    "Type of heating",
    "Type of glazing",
    "Elevator",
    "Number of facades",
    "Garden",
    "Surface garden",
    "Terrace",
    "Surface terrace",
    "Total land surface",
    "Swimming pool",
]


# Read the list
input_csv = "property_urls.csv"
with open(input_csv, "r", encoding="utf-8") as f:
    urls = []
    for line in f:
        line = line.strip()
        if line:
            urls.append(line)

# Scrape every url
all_specs = []
for url in urls:
    specs = {"url": url, "Property ID": url.rstrip("/").rsplit("/", 1)[-1]}
    # Property ID = everything after the last "/"
    soup = BeautifulSoup(requests.get(url,headers=headers).text, "html.parser")


    for li in soup.select("ul li"):
        txt = li.get_text(strip=True)
        price_table = re.match(r"^(.+?):\s*(.+)$", txt)
        if price_table:
            price_header = price_table.group(1)
            price_value = price_table.group(2)
            specs[price_header] = price_value

    for h4 in soup.select("h4"):
        p = h4.find_next("p")
        if p:
            if h4.get_text(strip=True) in KEEP:
                specs[h4.get_text(strip=True)] = p.get_text(strip=True)

    all_specs.append(specs)

    #for k, v in specs.items():
    #    if k in KEEP:
    #        print(f"{k}: {v}")

df = pd.DataFrame(all_specs)
df.to_csv("immovlan_final_file.csv", index=False)