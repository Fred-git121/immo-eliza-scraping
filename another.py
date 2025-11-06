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

# Function to scrape all property URLs
def scrape_property_urls():
    driver = webdriver.Firefox()  # Initialize driver
    all_property_urls = set()  # Using a set to avoid duplicates
    try:
        driver.get("https://immovlan.be/")  # Open homepage
        time.sleep(2)
        handle_cookie(driver)  # Accept cookies

        # Click language selection and search list buttons
        try:
            language_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/div[3]/a')))
            driver.execute_script("arguments[0].click();", language_button)
            time.sleep(2)

            search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "search-list-button")))
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(2)
        except:
            print("error")

        # Loop through pages and use for URL scraping
        for page_num in range(1, 51):
            url = f"https://immovlan.be/en/real-estate?isnewconstruction=only&page={page_num}&noindex=1"
            driver.get(url)
            handle_cookie(driver)
            time.sleep(2)  # Wait for page content to load

            # Parse page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract property URLs from buttons and links
            for a in soup.select("a.button.button-secondary, a[href*='/detail/'], a[href*='/projectdetail/']"):
                href = a.get("href")
                if href:
                    if "/projectdetail/" in href:
                        # For projectdetail, fetch the page and extract detail links
                        try:
                            project_soup = BeautifulSoup(requests.get(href, headers=get_random_headers(), timeout=10).text,"html.parser")
                            for link in project_soup.select("a[href*='/en/detail/']"):
                                prop_url = link.get("href")
                                if prop_url:
                                    all_property_urls.add(prop_url)
                        except:
                            continue
                    elif "/detail/" in href:
                        all_property_urls.add(href)

            print(f"Page {page_num}: {len(all_property_urls)} total properties")
            time.sleep(1)

    finally:
        driver.quit()  # Close browser

    # Save all scraped URLs to CSV
    with open("property_urls.csv", "w", encoding="utf-8") as f:
        for url in sorted(all_property_urls):
            f.write(url + "\n")
    print(f"Saved {len(all_property_urls)} property URLs")
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
    # Step 1: Scrape all property URLs
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
    with open("immovlan_final_file.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for specs in all_specs:
            for k, v in specs.items():
                if k in KEEP:  # Only write keys specified in KEEP
                    writer.writerow([k, v])

    print(f"\nFinished scraping {len(all_specs)} properties. Saved to immovlan_final_file.csv")
