import requests
from bs4 import BeautifulSoup
import random
import pandas

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

url = "https://immovlan.be/fr/immobilier?transactiontypes=a-vendre,en-vente-publique&noindex=1"
headers = {'User-Agent': random.choice(user_agents)}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, 'html.parser')

listings = []

for card in soup.find_all("article", class_="list-view-item"):
    id = card.find().get_text(strip=True)
    title = card.select_one("h2.card-title a").get_text(strip=True)
    price = card.select_one("strong.list-item-price").get_text(strip=True)
    locality= card.select_one("span[itemprop='addressLocality']").get_text(strip=True)
    link = card.select_one("h2.card-title a")["href"]
    vlncode = link.rstrip("/").split("/")[-1]

    listings.append({
        'id': vlncode,
        "title": title,
        "price": price,
        "Locality": locality
    })

# Print results
for item in listings:
    print(item)
# first_card = soup.find("article", class_="list-view-item")
# print(first_card.prettify())