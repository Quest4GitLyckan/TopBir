from selenium import webdriver
from selenium.webdriver.common.by import By
from googlesearch import search
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import requests
from dataclasses import dataclass

#skapa drivermeme
MyService = Service(ChromeDriverManager().install())
SystembolagDriver: webdriver = webdriver.Chrome(service=MyService)

#datan
@dataclass
class product_t:
    name: str
    brewery: str
    price: str #TODO konvertera till inte memeformat
    size: str
    style: str
    country: str
    alcVol: str
    score: str
    ratingAmounts: str
    #TODO spara bild för att visa i UI

BeerData = [] #TODO typa(Kanske inte behövs)??

def AgeCheck():
    SystembolagDriver.get("https://www.systembolaget.se/sortiment/ol/") #TODO parsa för egen butik/Kategori osv 
    time.sleep(5) #TODO RACE CONDITION
    AgeCheck = SystembolagDriver.find_element(By.XPATH, '/html/body/div[3]/section/div/div/div[3]/a[2]')
    AgeCheck.click()
    time.sleep(5) #TODO RACE CONDITION
    CookieCheck = SystembolagDriver.find_element(By.XPATH, '/html/body/div[6]/div[3]/div/div/button[2]')
    CookieCheck.click()

def LoadWholePage(): #AI genererad BEWARE
    last_height = SystembolagDriver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll to the bottom
        SystembolagDriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new products to render
        time.sleep(2) #TODO RACE CONDITION
        
        # Calculate new scroll height and compare with last scroll height
        new_height = SystembolagDriver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break # We reached the bottom
        else:
            last_height = new_height

def FetchProducts():
    html = SystembolagDriver.page_source
    soup = BeautifulSoup(html, "html.parser")
    ProductCards = soup.select('a.bg-white.border-1.shadow-md')
    
    try:
        for card in ProductCards:

            style_element = card.select_one('p[class*="caption-175"]')
            NewStyle = style_element.text.strip() if style_element else "Unknown style"

            price_element = card.select_one('p[class*="sans-strong-175"]')
            NewPrice = price_element.text.strip() if price_element else "Unknown price"

            name_elements = card.select('p[class*="monopol-250"]')

            if len(name_elements) == 2:
                NewBrewery = name_elements[0].text.strip()
                NewName = name_elements[1].text.strip()

            elif len(name_elements) == 1:
                NewBrewery = "N/A" 
                NewName = name_elements[0].text.strip()

            else:
                NewBrewery = "Unknown brewery"
                NewName = "Unknown Name"

            countryVolumeAlcSize_elements = card.select('p[class*="sans-175"]')
            
            if len(countryVolumeAlcSize_elements) >= 3:
                NewCountry = countryVolumeAlcSize_elements[1].text.strip()
                NewSize = countryVolumeAlcSize_elements[2].text.strip()
                NewAlcVol = countryVolumeAlcSize_elements[3].text.strip()
            else:
                NewCountry = "Anomalus country, vol or alc"
                NewSize = "Anomalus country, vol or alc"
                NewAlcVol = "Anomalus country, vol or alc"

            NewBeer = product_t(
                name = NewName,
                brewery = NewBrewery,
                price = NewPrice,
                size = NewSize, 
                style = NewStyle,
                country = NewCountry,
                alcVol = NewAlcVol,
                score = "NA",
                ratingAmounts = "NA"
            )
            BeerData.append(NewBeer)    
            
    except Exception as e:
        print(f"Skipped a product. Reason: {e}")

def fetchScore():
    for beer in BeerData:
        
        query = f'site:untappd.com/b/ "{beer.brewery}" "{beer.name}"'
        
        try:
            search_results = list(search(query, num=1, stop=1, pause=2))

            if not search_results:
                print("beer not found")
                return
                
            exact_url = search_results[0]

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(exact_url, headers=headers)
            
            if response.status_code == 200:
        
                soup = BeautifulSoup(response.text, 'html.parser')
                print(soup)
                NewScore = soup.select_one('span["class=num"]').text.strip()
                NewRatingAmount = soup.select_one('p["class=raters"]').text.strip()

                print(NewRatingAmount)
                print(NewScore)

                beer.score = NewScore
                beer.RatingAmounts = NewRatingAmount
                
        except Exception as e:
            return f"An error occurred: {e}"


def Main():

    AgeCheck()
    LoadWholePage() #HIttar en sida för tester
    FetchProducts()
    fetchScore()


    #while(True): #Hämtar ALLT
    #
    #    LoadWholePage()
    #    FetchProducts()
    #
    #    try:
    #        NextPageCheck = SystembolagDriver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div[2]/div[2]/div[2]/div[5]/div/a')
    #        NextPageCheck.click()
    #    except NoSuchElementException:
    #        break

    for beer in BeerData:
        print(beer)

Main()    


