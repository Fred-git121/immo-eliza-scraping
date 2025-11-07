#standard libraries
import time
import re
import csv
import random
import requests
import pandas as pd

#libraries for parsing HTML and automating browsers
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import for parallel processing
from concurrent.futures import ThreadPoolExecutor, as_completed

# Maximum number of threads for scraping property details concurrently
MAX_THREADS = 10

def get_random_headers():
    user_agents =[
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ]
    return {"User-Agent": random.choice(user_agents)}

def handle_cookie(driver):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
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
    all_links = []
    for p in range(1, MAX_SITE_PAGES + 1):
        batch = get_page(p, params_dict, label)
        if not batch:
            break
        all_links.extend(batch)
    print(f"{label} pages scraped: {len(all_links)} links")
    return all_links

# --------------- 4. RUN EVERYTHING (category-by-category) -------
all_links = []

for label, params in SALE_REGIONS.items():
    print(f"\n===== SCRAPING {label.upper()} =====")
    all_links.extend(scrape_category(params, label))

# --------------- 5. SAVE URLs -----------------------------------
df = pd.DataFrame(all_links, columns=["url", "province"]).drop_duplicates(subset="url")
df.to_csv("immovlan_sale.csv", index=False)
print(f"\nTotal unique links collected: {len(df)}")

# ============================================================
# ************ NEW: EXPAND PROJECTS ************
# ============================================================

def expand_projects(property_urls):
    """
    Take a list of URLs and expand any project URLs into individual properties
    Returns: list of individual property URLs (no projects)
    """
    driver = webdriver.Firefox()
    
    expanded_urls = set()
    project_count = 0
    property_count = 0
    
    try:
        for i, url in enumerate(property_urls, 1):
            # Make URL absolute if needed
            if url.startswith("/"):
                url = "https://www.immovlan.be" + url
            
            # Check if it's a project
            if "/projectdetail/" in url:
                project_count += 1
                print(f"\n[{i}/{len(property_urls)}] Expanding project: {url}")
                
                try:
                    driver.get(url)
                    handle_cookie(driver)
                    time.sleep(3)
                    
                    # Find all individual property links inside the project
                    property_links = driver.find_elements(
                        By.XPATH, 
                        "//a[contains(@href, '/en/detail/')]"
                    )
                    
                    # Extract and add individual property URLs
                    for link in property_links:
                        property_url = link.get_attribute("href")
                        if property_url:
                            expanded_urls.add(property_url)
                    
                    print(f"  → Found {len(property_links)} properties in this project")
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"  ✗ Error expanding project: {e}")
                    continue
                    
            elif "/detail/" in url:
                # It's already an individual property
                property_count += 1
                expanded_urls.add(url)
            
            # Progress update every 10 URLs
            if i % 10 == 0:
                print(f"Progress: {i}/{len(property_urls)} | Projects: {project_count} | Properties: {len(expanded_urls)}")
        
        print(f"\n{'='*60}")
        print(f"EXPANSION COMPLETE:")
        print(f"  Original URLs: {len(property_urls)}")
        print(f"  Projects found: {project_count}")
        print(f"  Direct properties: {property_count}")
        print(f"  Final property count: {len(expanded_urls)}")
        print(f"{'='*60}\n")
        
    finally:
        driver.quit()
    
    return list(expanded_urls)

# ============================================================
# ************ CONTINUE WITH EXISTING CODE ************
# ============================================================

def scrape_property_details(url):
    if url.startswith("/"):
        url = "https://www.immovlan.be" + url
    headers = get_random_headers()
    specs = {}
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers, timeout=10).text, "html.parser")
        specs["Property ID"] = url.rstrip("/").rsplit("/", 1)[-1]
        specs["url"] = url  # Add URL to specs
        
        for li in soup.select("ul li"):
            txt = li.get_text(strip=True)
            m = re.match(r"^(.+?):\s*(.+)$", txt)
            if m:
                specs[m.group(1)] = m.group(2)
        
        for h4 in soup.select("h4"):
            p = h4.find_next("p")
            if p:
                specs[h4.get_text(strip=True)] = p.get_text(strip=True)
    
    except Exception as e:
        print(f"Failed scraping {url}: {e}")
    return specs

# Main execution
if __name__ == "__main__":
    # Step 1: Get all URLs (already done above)
    property_urls = [url for url, _ in all_links]
    print(f"\nInitial URLs collected: {len(property_urls)}")
    
    # *** NEW STEP 2: Expand projects into individual properties ***
    print("\n" + "="*60)
    print("EXPANDING PROJECTS...")
    print("="*60)
    
    expanded_property_urls = expand_projects(property_urls)
    
    # Save expanded URLs
    pd.DataFrame(expanded_property_urls, columns=["url"]).to_csv(
        "immovlan_expanded_urls.csv", 
        index=False
    )
    print(f"✓ Expanded URLs saved to immovlan_expanded_urls.csv")
    
    # Step 3: Scrape property details concurrently
    print("\n" + "="*60)
    print("SCRAPING PROPERTY DETAILS...")
    print("="*60 + "\n")
    
    all_specs = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_url = {
            executor.submit(scrape_property_details, url): url 
            for url in expanded_property_urls
        }
        
        for future in as_completed(future_to_url):
            specs = future.result()
            if specs:
                all_specs.append(specs)
            print(f"Scraped {len(all_specs)}/{len(expanded_property_urls)} properties", end='\r')
    
    print(f"\n\n✓ Scraped {len(all_specs)} properties")
    
    # Step 4: Save using Pandas (better format than your original)
    df_final = pd.DataFrame(all_specs)
    
    # Keep only columns in KEEP list (if they exist)
    columns_to_keep = [col for col in KEEP if col in df_final.columns]
    df_final = df_final[columns_to_keep]
    
    df_final.to_csv("immovlan_final_file.csv", index=False, encoding="utf-8")
    
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE!")
    print(f"  Total properties scraped: {len(all_specs)}")
    print(f"  Saved to: immovlan_final_file.csv")
    print(f"{'='*60}")