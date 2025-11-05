from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv

# 1. Chrome aç
driver = webdriver.Chrome()

# 2. Tek ilan sayfasına git
url = "https://www.immovlan.be/en/classified/house-for-sale/[TEK-ILAN-ID]"
driver.get(url)
time.sleep(3)

# 3. Cookie izni
cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
cookie_button.click()
time.sleep(1)

# 4. Sayfanın HTML'ini al
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 5. Bilgileri çek (CSS selector kullanıyoruz)
title = soup.select_one("h1").text
price = soup.select_one("span.classified-price").text
rooms = soup.select_one("span.classified-rooms").text
living_area = soup.select_one("span.classified-living-area").text

# 6. CSV dosyasına yaz
with open("ilan.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Başlık satırı
    writer.writerow(["Başlık", "Fiyat", "Oda Sayısı", "Yaşam Alanı"])
    
    # İlan verisi
    writer.writerow([title, price, rooms, living_area])

print("İlan CSV dosyasına kaydedildi!")

# 7. Tarayıcıyı kapat
driver.quit()