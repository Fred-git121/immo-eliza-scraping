#standard libraries
import time  # For adding delays between actions
import re  # For regular expressions
import csv  # For reading/writing CSV files
import random  # For selecting random values (used for user-agent rotation)
import requests  # For sending HTTP requests

#libraries for parsing HTML and automating browsers
from bs4 import BeautifulSoup  # For parsing HTML content
from selenium import webdriver  # For controlling a browser programmatically
from selenium.webdriver.common.by import By  # For locating elements in Selenium
from selenium.webdriver.support.ui import WebDriverWait  # For waiting for elements to appear
from selenium.webdriver.support import expected_conditions as EC  # For waiting conditions in Selenium

# Import for parallel processing
from concurrent.futures import ThreadPoolExecutor, as_completed  # For multithreading

# Maximum number of threads for scraping property details concurrently
MAX_THREADS = 5

# Define which property details we want to keep when saving CSV
KEEP = {
    "Property ID",
    "city-line",
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
}

# Define all the search URLs to scrape
SEARCH_URLS = [
    "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=house&minbedrooms=1&maxbedrooms=1&isnewconstruction=no",
    "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=house&minbedrooms=2&maxbedrooms=2&isnewconstruction=no",
    "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=house&minbedrooms=3&maxbedrooms=3&isnewconstruction=no",
    "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=house&minbedrooms=4&maxbedrooms=4&isnewconstruction=no",
    "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=house&tags=hasgarden&isnewconstruction=no",
    "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=house&tags=hasterrace&isnewconstruction=no",
]

# Function to return random headers
def get_random_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    return {"User-Agent": random.choice(user_agents)}

# Function to handle cookie popup on the website using Selenium
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

# Function to scrape all property URLs from multiple search URLs
def scrape_property_urls():
    all_property_urls = set()

    # Loop through each search URL
    for search_idx, base_url in enumerate(SEARCH_URLS, 1):
        print(f"\n=== Scraping search URL {search_idx}/{len(SEARCH_URLS)} ===")
        
        # Loop through pages for each search URL
        for page_num in range(1, 51):
            url = f"{base_url}&page={page_num}&noindex=1"
            print(f"Fetching page {page_num} ...")

            try:
                r = requests.get(url, headers=get_random_headers(), timeout=15)
                r.raise_for_status()
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            # Find property links (only individual listings)
            found_on_page = 0
            for a in soup.select("a[href*='/detail/']"):
                href = a.get("href")
                if not href:
                    continue

                if href.startswith("/"):
                    href = "https://immovlan.be" + href

                if href not in all_property_urls:
                    all_property_urls.add(href)
                    found_on_page += 1

            print(f"Page {page_num}: Found {found_on_page} new properties | Total: {len(all_property_urls)}")
            
            # If no properties found on this page, likely reached the end
            if found_on_page == 0:
                print(f"No new properties found on page {page_num}, moving to next search URL...")
                break
            
            time.sleep(random.uniform(0.5, 1.5))  # be polite

    # Save all scraped URLs to CSV
    with open("house_sale_urls.csv", "w", encoding="utf-8") as f:
        for url in sorted(all_property_urls):
            f.write(url + "\n")
    print(f"\n=== Saved {len(all_property_urls)} unique property URLs ===")
    return list(all_property_urls)

# Function to scrape property details from a single property URL using BeautifulSoup
def scrape_property_details(url):
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
    # Step 1: Scrape all property URLs from all search URLs
    property_urls = scrape_property_urls()

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
    with open("immovlan_house_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for specs in all_specs:
            for k, v in specs.items():
                if k in KEEP:  # Only write keys specified in KEEP
                    writer.writerow([k, v])

    print(f"\nFinished scraping {len(all_specs)} properties. Saved to immovlan_house_sales.csv")