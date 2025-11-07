import requests, pandas as pd, re, random, csv
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---------------------------------------------------------
# Function: get_random_headers()
# Purpose: Returns a random User-Agent to avoid being
# blocked by anti-bot security
# ---------------------------------------------------------
def get_random_headers():
    user_agents =[
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ]
    return {"User-Agent": random.choice(user_agents)}
# Initialize a random header for all requests
headers = get_random_headers()

# ---------------------------------------------------------
# List of columns that will be kept in the final CSV output
# ---------------------------------------------------------
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
    "Swimming pool"
]

# ---------------------------------------------------------
# 1. Read the list URLS from a CSV file
# Each line in the CSV file should contain one URL
# ---------------------------------------------------------
input_csv_file = "immovlan_sale.csv"

property_urls = []
with open(input_csv_file, "r", encoding="utf-8") as file:
    for line in file:
        cleaned_line = line.strip()
        if cleaned_line:
            property_urls.append(cleaned_line)

# ---------------------------------------------------------
# 2. Loop through each property URL and scrape details
# ---------------------------------------------------------
all_property_data = []
for property_url in tqdm(property_urls, desc="Scraping"):
    # Initialize a dictionary to store all scraped specs
    property_data = {"url": property_url}

    # Extract Property ID (the last part of the URL)
    property_data["Property ID"] = property_url.rstrip("/").rsplit("/", 1)[-1]

    # Fetch the webpage content
    response = requests.get(property_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # -----------------------------------------------------
    # Extract <ul><li> pairs formatted as "Label: Value
    # -----------------------------------------------------
    for list_item in soup.select("ul li"):
        text = list_item.get_text(strip=True)
        match = re.match(r"^(.+?):\s*(.+)$", text)
        if match:
            field_name = match.group(1)
            price_value = match.group(2)
            property_data[field_name] = price_value

    # -----------------------------------------------------
    # Extract <h4>Field name</h4><p>Field value</p> pairs
    # Only keep fields that are in COLUMNS_TO_KEEP
    # -----------------------------------------------------
    for field_heading in soup.select("h4"):
        field_value_element = field_heading.find_next("p")
        if field_value_element:
            field_name = field_heading.get_text(strip=True)
            if field_name in COLUMNS_TO_KEEP:
                property_data[field_name] = field_value_element.get_text(strip=True)

    # Add the property specs to the main list
    all_property_data.append(property_data)

# ---------------------------------------------------------
# 3. Convert collected data into a DataFrame and export CSV
# ---------------------------------------------------------
output_csv_file = "immovlan_final_file.csv"
df = pd.DataFrame(all_property_data)
df.to_csv(output_csv_file, index=False)