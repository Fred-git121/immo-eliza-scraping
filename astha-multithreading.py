from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time

# ============ SHARED DATA (Thread-safe) ============
all_property_urls = set()
url_lock = Lock()

# ============ FUNCTIONS ============

def handle_cookie(driver):
    """Cookie handler - take driver as parameter"""
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
        pass

def scrape_page(page_num):
    """
    Scrape one page - this runs in parallel for each page
    Each thread gets its own browser
    """
    # Create browser for this thread
    driver = webdriver.Firefox()
    
    try:
        # Navigate to page
        url = f"https://immovlan.be/en/real-estate?isnewconstruction=only&page={page_num}&noindex=1"
        driver.get(url)
        handle_cookie(driver)
        time.sleep(3)
        
        # Find all buttons on this page
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.button-secondary")
        
        property_urls = []
        for button in all_buttons:
            href = button.get_attribute("href")
            if href and ("/detail/" in href or "/projectdetail/" in href):
                property_urls.append(href)
        
        # Process each URL for individual projects
        for url_item in property_urls:
            if "/projectdetail/" in url_item:
                try:
                    driver.get(url_item)
                    handle_cookie(driver)
                    time.sleep(3)
                    
                    property_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/en/detail/')]")
                    
                    for link in property_links:
                        property_url = link.get_attribute("href")
                        if property_url:
                            # Thread-safe adding
                            with url_lock:
                                all_property_urls.add(property_url)
                    
                    time.sleep(2)
                except:
                    continue
                    
            elif "/detail/" in url_item:
                # Thread-safe adding
                with url_lock:
                    all_property_urls.add(url_item)
        
        # Output per page
        print(f"Page {page_num}: {len(all_property_urls)} total properties")
        
    except Exception as e:
        print(f"Error on page {page_num}: {e}")
        
    finally:
        # Always close this thread's browser
        driver.quit()

# ============ MAIN PROGRAM ============

if __name__ == "__main__":
    # Initial navigation (done once, not per thread)
    print("Starting initial navigation...")
    initial_driver = webdriver.Firefox()
    
    try:
        initial_driver.get("https://immovlan.be/")
        time.sleep(2)
        handle_cookie(initial_driver)
        
        # Click language and search buttons
        try:
            language_button = WebDriverWait(initial_driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/div[3]/a'))
            )
            initial_driver.execute_script("arguments[0].click();", language_button)
            time.sleep(2)
            
            search_button = WebDriverWait(initial_driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "search-list-button"))
            )
            initial_driver.execute_script("arguments[0].click();", search_button)
            time.sleep(2)
        except:
            print(" Navigation failed, but continuing...")
    finally:
        initial_driver.quit()
    
    # Main scraping with multithreading
    print("\n Starting multithreaded scraping with 5 browsers...\n")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(scrape_page, range(1, 6))
    
    # Final result
    print(f"\n Final Total: {len(all_property_urls)} unique properties")
    
    # Save to CSV
    # with open("property_urls.csv", "w", encoding="utf-8") as f:
    #     for url in sorted(all_property_urls):
    #         f.write(url + "\n")
    
    # print(" Saved to property_urls.csv")