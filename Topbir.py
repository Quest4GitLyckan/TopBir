from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

MyService = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=MyService)

#Ålderscheck
driver.get("https://www.systembolaget.se/sortiment/ol/")
time.sleep(2)
AgeCheck = driver.find_element()
