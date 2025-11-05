from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time

driver = webdriver.Firefox()

# Simple cookie handler
def handle_cookie():
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
        pass  # No cookie popup, continue

# Initial navigation
driver.get("https://immovlan.be/")
time.sleep(2)
handle_cookie()

# Click language and search buttons
try:
    language_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/div[3]/a'))
    )
    driver.execute_script("arguments[0].click();", language_button)
    time.sleep(2)
    
    search_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "search-list-button"))
    )
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(2)
except:
    print(" Navigation failed, but continuing...")


# Main Scraping
all_property_urls = set()                # Use a SET to automatically prevent duplicates

try:
    for page_num in range(1, 51):
        url = f"https://immovlan.be/en/real-estate?isnewconstruction=only&page={page_num}&noindex=1"
        driver.get(url)
        handle_cookie()
        time.sleep(3) # Wait for page to load
        
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
                    time.sleep(3)
                    
                    property_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/en/detail/')]")
                    
                    for link in property_links:
                        property_url = link.get_attribute("href")
                        if property_url:
                            all_property_urls.add(property_url)
                    
                    time.sleep(2)
                except:
                    continue
            elif "/detail/" in url_item:
                all_property_urls.add(url_item)
        
        # Output per page
        print(f"Page {page_num}: {len(all_property_urls)} total properties")
        time.sleep(2)
    
    # Final result
    print(f"\nFinal Total: {len(all_property_urls)} unique properties")

finally:
    driver.quit()

# Save to CSV
with open("property_urls.csv", "w", encoding="utf-8") as f:
    for url in sorted(all_property_urls):
        f.write(url + "\n")

print(" Saved to property_urls.csv")



