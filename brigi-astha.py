from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import requests
from bs4 import BeautifulSoup

# ---- small helpers ----
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]
def headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def polite_sleep(a=0.6, b=1.4):
    time.sleep(random.uniform(a, b))

def expand_project_with_bs(project_url: str) -> list:
    """Requests + BeautifulSoup to turn a /projectdetail/ page into /detail/ links."""
    out = []
    try:
        r = requests.get(project_url, headers=headers(), timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/detail/" in href:
                # make absolute if needed
                if href.startswith("/"):
                    href = "https://immovlan.be" + href
                out.append(href)
    except Exception as e:
        print(f"[warn] expand failed {project_url}: {e}")
    return out

# (optional) accept cookies if the banner appears
def accept_cookies_if_present(driver):
    try:
        btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        driver.execute_script("arguments[0].click();", btn)
        polite_sleep()
    except:
        pass

driver = webdriver.Firefox()
all_property_urls = set()  # Use a SET to automatically prevent duplicates

try:
    # open home once to clear cookie banner if any
    driver.get("https://immovlan.be/")
    accept_cookies_if_present(driver)

    for page_num in range(1, 51):
        url = f"https://immovlan.be/en/real-estate?isnewconstruction=only&page={page_num}&noindex=1"
        driver.get(url)

        # wait for any link containing /detail/ or /projectdetail/
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@href, '/detail/') or contains(@href, '/projectdetail/')]")
                )
            )
        except:
            print(f"Page {page_num}: no property anchors detected (skipping)")
            continue

        # collect candidate links (broader than a specific button class)
        anchors = driver.find_elements(By.TAG_NAME, "a")
        property_urls = []
        for a in anchors:
            href = a.get_attribute("href")
            if not href:
                continue
            if "/detail/" in href or "/projectdetail/" in href:
                property_urls.append(href)

        # Process each URL for individual projects
        for url_item in property_urls:
            if "/projectdetail/" in url_item:
                # >>> use requests + BeautifulSoup here instead of Selenium navigation <<<
                expanded = expand_project_with_bs(url_item)
                if expanded:
                    all_property_urls.update(expanded)
                polite_sleep()
            elif "/detail/" in url_item:
                all_property_urls.add(url_item)

        # Output per page
        print(f"Page {page_num}: {len(all_property_urls)} total properties")
        polite_sleep()

    # Final result
    print(f"\nFinal Total: {len(all_property_urls)} unique properties")

finally:
    driver.quit()

# # Save to CSV
# with open("property_urls.csv", "w", encoding="utf-8") as f:
#     for url in sorted(all_property_urls):
#         f.write(url + "\n")

# print("Saved to property_urls.csv")
