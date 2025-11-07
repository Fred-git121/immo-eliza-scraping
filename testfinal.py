#standard libraries
import time  # For adding delays between actions
import re  # For regular expressions
import csv  # For reading/writing CSV files
import random  # For selecting random values (used for user-agent rotation)
import requests  # For sending HTTP requests
import pandas as pd

#libraries for parsing HTML and automating browsers
from bs4 import BeautifulSoup  # For parsing HTML content
from selenium.webdriver.common.by import By  # For locating elements in Selenium
from selenium.webdriver.support.ui import WebDriverWait  # For waiting for elements to appear
from selenium.webdriver.support import expected_conditions as EC  # For waiting conditions in Selenium

# Import for parallel processing
from concurrent.futures import ThreadPoolExecutor, as_completed  # For multithreading

# Maximum number of threads for scraping property details concurrently
MAX_THREADS = 5

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

def handle_cookie(driver):
    try:
        # Wait until the cookie accept button appears (max 3 seconds)
        button = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "didomi-notice-agree-button")))
        # Click the button
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)  # Small delay after clicking
    except:
        # If the button is not found, ignore
        pass
BASE = "https://www.immovlan.be/en/real-estate"

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

# The columns that will be kept in the final file
COLUMNS_TO_KEEP = [
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

# --------------- 2. GRAB ONE PAGE --------------------------
def get_page(page, params_dict, label):
    params = {**params_dict, "page": page}
    r = requests.get(BASE, params=params, headers=get_random_headers(), timeout=10)
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

# Function to scrape property details from a single property URL using BeautifulSoup
def scrape_property_details(url):
    if url.startswith("/"):
        url = "https://www.immovlan.be" + url
    headers = get_random_headers()  # Use random headers for request
    specs = {}  # Dictionary to store property details
    try:
        # Fetch the page HTML and parse with BeautifulSoup
        soup = BeautifulSoup(requests.get(url, headers=headers, timeout=10).text, "html.parser")
        specs["Property ID"] = url.rstrip("/").rsplit("/", 1)[-1]  # Property ID from URL

        # Extract property details from <li> elements
        for li in soup.select("ul li"):
            txt = li.get_text(strip=True)
            m = re.match(r"^(.+?):\s*(.+)$", txt)  # Match "Key: Value"
            if m:
                specs[m.group(1)] = m.group(2)

        # Extract property details from <h4> followed by <p>
        for h4 in soup.select("h4"):
            p = h4.find_next("p")
            if p:
                specs[h4.get_text(strip=True)] = p.get_text(strip=True)

    except Exception as e:
        print(f"Failed scraping {url}: {e}")
    return specs

# Main execution
if __name__ == "__main__":
    # Step 1: Scrape all property URLs
    property_urls = [url for url, _ in all_links]


    # Step 2: Scrape property details concurrently using ThreadPoolExecutor
    all_specs = []    #it will store the results scraped
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:       #creating a thread pool, specifying how many threads, executor->handling multiple functions, 'with' is gonna close it after
        #looping over all urls, executor schedules the function to run in a seperate thread
        future_to_url = {executor.submit(scrape_property_details, url): url for url in property_urls}
        for future in as_completed(future_to_url):
            specs = future.result()
            if specs:
                all_specs.append(specs)
            print(f"Scraped {len(all_specs)}/{len(property_urls)} properties", end='\r')

    # Step 3: Save the scraped property details to a CSV file
    with open("immovlan_final_file.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for specs in all_specs:
            for k, v in specs.items():
                if k in KEEP:  # Only write keys specified in KEEP
                    writer.writerow([k, v])

    print(f"\nFinished scraping {len(all_specs)} properties. Saved to immovlan_final_file.csv")