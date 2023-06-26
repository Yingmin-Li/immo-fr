# Imports
from bs4 import BeautifulSoup as soup
from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


from urllib.request import urlopen as uReq

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


def getCheapestAd(ads):
    cheapestPrice = ads[0].numPrice
    cheapest = ""
    for a in ads:
        if a.numPrice < cheapestPrice:
            cheapestPrice = a.numPrice
    print(cheapestPrice)

def getPageSoupFromFile(path):
    file = open(path, "r")
    r = file.read()
    return (soup(r, "html.parser"))

def getPageSoupFromUrl(url):



    # Configure Chrome options to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set the path to your Chrome WebDriver
    webdriver_path = '/path/to/chromedriver'

    # Create a new Chrome driver instance
    driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)

    # Load the page with JavaScript and cookies requirement
    driver.get('https://example.com')

    # Continue processing the page using Selenium
    # For example, you can retrieve the page source or interact with elements

    page_source = driver.page_source
    print(page_source)

# After finishing, close the browser
driver.quit()

    # Set necessary headers to mimic JavaScript behavior
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Referer': url,
    }

    # Create a session object
    session = requests.Session()

    # Make a GET request
    response = session.get(url, headers=headers, allow_redirects=False)

    print(response.status_code)

    # Check if the response requires a redirect
    if response.status_code == 302:
        redirect_url = response.headers['Location']

        # Make another GET request to the redirect URL
        r = session.get(redirect_url, headers=headers)

        soup1 = soup(r.content, 'html.parser')

        print(soup1)
        return (soup1)
    return None

def getAdsFromSelogerPage(url):
    #page_soup = getPageSoupFromFile("./html/raw-pap.html")
    page_soup = getPageSoupFromUrl(url)
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


#todo make a container class?
#todo sort by most rentable - price / m2 ?


# try:
ads = getAdsFromSelogerPage('https://www.pap.fr/annonce/vente-appartements-hauts-de-seine-92-g456g43343g43706-2-pieces-a-partir-de-1-chambres-jusqu-a-330000-euros-entre-30-et-50-m2')
#ads = getAdsFromSelogerPage("./raw.html")
ads.sort(key = lambda x: x.numPrice)
print("Top 3 cheapest ads:")
for a in ads:
    a.dumpAll()
