from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as soup
from bs4 import BeautifulSoup
import requests
import csv

import time
import json
import pandas as pd

from setupLogger import ScrapLogger

# Define urls
PAP_URL='https://www.pap.fr/annonce/vente-appartements-hauts-de-seine-92-g456g43343g43706-2-pieces-a-partir-de-1-chambres-jusqu-a-330000-euros-entre-30-et-50-m2'

# Defind pap html page
PAP_ADS_HTML_FILE='PAP_ADS_0.html'

# Set the path to your Chrome WebDriver
webdriver_path = 'D:\\tools\\chromedriver_win32\\chromedriver.exe'

# Define reference data path
PAP_APPT_ON_SALE_CSV = 'src/pap_appt_on_sale_sell.csv'

# Container Class that stores an ad's values
class AdContainer(object):
    def __init__(self, city, post_code, piece, badrooms, price,surface,link, desc):
        self.city = city
        self.post_code = post_code
        self.piece = piece
        self.badrooms = badrooms
        self.price = price
        self.numPrice = int(price[0:3])
        self.size = surface
        self.link = link
        self.desc = desc

    def dump(self):
        print("City: " + str(self.city) + "\tpost_code: " + str(self.post_code) + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) + "\tlink: " + str(self.link))

    def dumpAll(self):
        print("City: " + str(self.city) + "\tpost_code: " + str(self.post_code) + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) + "\tlink: " + str(self.link))



class PAPScrapper():

    def __init__(self):
        super().__init__()

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("PAPScrapper")

        # Configure Chrome options
        self.chrome_options = Options()
        self.userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
        self.chrome_options.add_argument(f'user-agent={self.userAgent},referer={PAP_URL}')

        # Create a new Chrome driver instance
        self.service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def getPageSoupFromFile(path):
        file = open(path, "r")
        r = file.read()
        return (soup(r, "html.parser"))

    def scrap(self):
        # Load the page with JavaScript and cookies requirement
        self.driver.get(PAP_URL)



        # Continue without accepting cookie
        cookie_deny = self.driver.find_element(By.CLASS_NAME, "sd-cmp-3ScGE")
        cookie_deny.click()

        # Save html content to file
        with open("src/"+PAP_ADS_HTML_FILE, "w", encoding='utf-8') as f:
            f.write(self.driver.page_source)

        # parse ads
        html = self.driver.page_source
        self.parseAd(html)


    def parseAd(self,html):
        #page_soup = getPageSoupFromFile("src/raw-pap.html")
        page_soup = BeautifulSoup(html)
        ads = []

        #print(page_soup)
        containers = page_soup.findAll("div", {"class":"row row-large-gutters page-item"})[0].findAll("div", {"class":"search-list-item-alt"})
        print(len(containers))

        for container in containers:
            #print(container)
            city = ""
            post_code = 0
            badrooms=0
            piece=0
            surface=0

            price = container.findAll("span", {"class":"item-price"})

            if ("€" in price[0].text ):
                city_pc = container.findAll("a", {"class":"item-title"})[0].findAll("span", {"class":"h1"})[0].text
                city = city_pc.split("(")[0].strip()

                if len(city_pc.split("(")) >1:
                  post_code = city_pc.split("(")[1].split(")")[0].strip()
                tags_parent = container.findAll("ul", {"class":"item-tags"})

                if len(tags_parent) >0 :
                    tags = tags_parent[0].findAll("li")
                    for tag in tags:
                        if ( " pièces" in tag ):
                            piece = tag
                        elif ( " chambre" in tag ):
                            badrooms = tag
                        elif ( " m2" in tag.text ):
                            surface = tag.text

                price = container.findAll("span", {"class":"item-price"})[0].text.split('(')[0].strip()
                link = container.findAll("a", {"class":"item-title"})[0]['href']
                desc = container.findAll("p", {"class":"item-description"})
                print(city_pc)
                print(price)

                ads.append(AdContainer(city, post_code, piece, badrooms, price,surface,link, desc))


        return ads

if __name__ == "__main__":
    papScrapper = PAPScrapper()
    papScrapper.scrap()
