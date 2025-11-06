import time
import random
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

def handle_cookie(driver):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
        pass

def choose_language(driver):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/div[3]/a'))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
        pass

def click_search_list(driver):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "search-list-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
    except:
        pass

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

def get_random_headers():
    return {'User-Agent': random.choice(user_agents)}

def scrape_property(url):
    headers = get_random_headers()
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
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
        specs["URL"] = url
        print(f"Scraped: {url}")
        return specs
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return {"URL": url, "Error": str(e)}

def expand_project_selenium(url, driver):
    """Use Selenium to expand /projectdetail/ URLs into individual property URLs"""
    urls = []
    if "/projectdetail/" in url:
        try:
            driver.get(url)
            time.sleep(2)
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/en/detail/')]")
            for link in links:
                href = link.get_attribute("href")
                if href:
                    urls.append(href)
        except:
            pass
    else:
        urls.append(url)
    return urls


driver = webdriver.Chrome()
driver.get("https://immovlan.be/")
handle_cookie(driver)
choose_language(driver)
click_search_list(driver)

all_property_urls = set()
try:
    for page_num in range(1, 51):
        page_url = f"https://immovlan.be/en/real-estate?isnewconstruction=only&page={page_num}&noindex=1"
        driver.get(page_url)
        handle_cookie(driver)
        time.sleep(2)

        buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.button-secondary")
        for button in buttons:
            href = button.get_attribute("href")
            if href:
                expanded = expand_project_selenium(href, driver)
                all_property_urls.update(expanded)

        print(f"Page {page_num}: {len(all_property_urls)} properties collected so far")
        time.sleep(1)
finally:
    driver.quit()

print(f"\nTotal unique properties to scrape: {len(all_property_urls)}")

all_specs = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(scrape_property, url) for url in all_property_urls]
    for future in as_completed(futures):
        all_specs.append(future.result())


df = pd.DataFrame(all_specs)
df.to_csv("immovlan_final_file.csv", index=False)
print("Saved CSV file successfully.")
