from selenium import webdriver                                    #to start the browser
from selenium.webdriver.common.by import By                       #how to find elements (by XPATH, by ID..)
from selenium.webdriver.support.ui import WebDriverWait           #waiting for elements to be clickable + EC
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import TimeoutException           #in case an element is not found in time
import time                                                       #optional delay to avoid getting banned, wait for popups


#set up the WebDriver, start Chrome
driver = webdriver.Chrome()

#open the website
driver.get("https://immovlan.be/")

#locate where we have to click using XPath
language_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[3]/a')

#click the link
language_button.click()

#delay so the popup has time to appear before clicking
time.sleep(2)

#waiting 3 seconds for the popup to appear, locating it by ID, then clicking it
try:
    accept_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
    accept_button.click()
except TimeoutException:
    print("timed out")


#clicking on the search list button, identified by the class name
search_list_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, "search-list-button")))
search_list_button.click()

time.sleep(2)

all_property_urls = []

#findig all property on the first page (<article>)
articles = driver.find_elements(By.CSS_SELECTOR, "article.list-view-item")     #locating elements
#extracting the url of each property                                           #tag is <article> for a section, class=list-view-item
property_urls = []                                                             #article element that has the class list-view-item
for article in articles:
    url = article.get_attribute("data-url") #stores the property url
    property_urls.append(url)
#looping through and opening to scrape
for url in property_urls:
    driver.get(url)
    time.sleep(2)

'''Scrape



        right

        

                here'''


all_property_urls.extend(property_urls)  #storing urls here

#we loop through the 51 pages, we extend the url name with the page number, and get the url (page 1 already done)

for page_number in range(2, 51):
    url = f"https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&noindex=1&page={page_number}"
    driver.get(url)
    time.sleep(2)
#finding all properties in the page, and storing it in a list
    articles = driver.find_elements(By.CSS_SELECTOR, "article.list-view-item")    #locating elements
    property_urls = []                                                            #tag is <article> for a section, class=list-view-item
    for article in articles:                                                      #article element that has the class list-view-item
        url = article.get_attribute("data-url")  #stores the property url
        property_urls.append(url)

 #looping through and opening to scrape
    for url in property_urls:
        driver.get(url)
        time.sleep(2)

        '''Scrape
                
        

                    right
                            
                    

                                here'''

    all_property_urls.extend(property_urls) #storing urls here

#waiting before closing
time.sleep(5)
#close the browser when done
driver.close()