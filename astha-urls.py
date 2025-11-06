from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Firefox()
all_property_urls = set()

def handle_cookie():
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
        pass

def apply_filters(transaction, property_type):
    """Click checkboxes to apply filters"""
    
    # Go to search page
    driver.get("https://immovlan.be/en/search")
    handle_cookie()
    time.sleep(2)
    
    # Click transaction type checkbox
    try:
        trans_checkbox = driver.find_element(By.ID, f"checkbox-transaction-type-{transaction}")
        if not trans_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", trans_checkbox)
            time.sleep(0.5)
    except Exception as e:
        print(f"Could not select transaction: {e}")
        return False
    
    # Click property type checkbox
    try:
        prop_checkbox = driver.find_element(By.ID, f"_search_list_cb_ptype_{property_type}")
        if not prop_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", prop_checkbox)
            time.sleep(0.5)
    except Exception as e:
        print(f"Could not select property type: {e}")
        return False
    
    # Click search button
    try:
        search_button = driver.find_element(By.CSS_SELECTOR, "button.search-list-button, button[type='submit']")
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(3)
        return True
    except Exception as e:
        print(f"Could not click search: {e}")
        return False

# Filter combinations
filter_combinations = [
    {'transaction': 'sale', 'property': 'appartment', 'label': 'Apartments for Sale'},
    {'transaction': 'sale', 'property': 'house', 'label': 'Houses for Sale'},
    {'transaction': 'sale', 'property': 'entreprise', 'label': 'Businesses for Sale'},
    {'transaction': 'sale', 'property': 'land', 'label': 'Land for Sale'},
    {'transaction': 'sale', 'property': 'garage', 'label': 'Garages for Sale'},
    {'transaction': 'rent', 'property': 'appartment', 'label': 'Apartments for Rent'},
    {'transaction': 'rent', 'property': 'house', 'label': 'Houses for Rent'},
    {'transaction': 'rent', 'property': 'entreprise', 'label': 'Businesses for Rent'},
    {'transaction': 'rent', 'property': 'land', 'label': 'Land for Rent'},
    {'transaction': 'rent', 'property': 'garage', 'label': 'Garages for Rent'},
]

try:
    for filter_combo in filter_combinations:
        print(f"\n{'='*60}")
        print(f"Scraping: {filter_combo['label']}")
        print(f"{'='*60}\n")
        
        # Apply filters
        if not apply_filters(filter_combo['transaction'], filter_combo['property']):
            print("Failed to apply filters, skipping...")
            continue
        
        # Get base URL after filters applied
        base_url = driver.current_url.split('?')[0] + '?' + driver.current_url.split('?')[1]
        
        # Loop through pages
        for page_num in range(1, 51):
            # Navigate to specific page
            if page_num == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}&page={page_num}"
            
            driver.get(page_url)
            time.sleep(3)
            
            # Find all buttons
            all_buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.button-secondary")
            
            if len(all_buttons) == 0:
                print(f"  No results on page {page_num}")
                break
            
            property_urls = []
            for button in all_buttons:
                href = button.get_attribute("href")
                if href and ("/detail/" in href or "/projectdetail/" in href):
                    property_urls.append(href)
            
            # Process URLs
            for url_item in property_urls:
                if "/projectdetail/" in url_item:
                    try:
                        driver.get(url_item)
                        handle_cookie()
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
            
            print(f"  Page {page_num}: {len(all_property_urls)} total")
            time.sleep(2)
        
        print(f"\n✓ {filter_combo['label']}: {len(all_property_urls)} total so far\n")
    
    print(f"\n{'='*60}")
    print(f"Final Total: {len(all_property_urls)} unique properties")
    print(f"{'='*60}\n")

finally:
    driver.quit()

with open("property_urls_10k.csv", "w", encoding="utf-8") as f:
    for url in sorted(all_property_urls):
        f.write(url + "\n")

print("✅ Saved to property_urls_10k.csv")