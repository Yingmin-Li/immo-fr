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
from csv import writer

import os
from PIL import Image
from urllib.parse import urlparse, unquote
from pathlib import Path

import time
import json
import pandas as pd
import re

from setupLogger import ScrapLogger

# Define urls
PAP_URL='https://www.pap.fr/annonce/vente-appartements-hauts-de-seine-92-g456g43343g43706-2-pieces-a-partir-de-1-chambres-jusqu-a-330000-euros-entre-30-et-50-m2'
PAP_BASE_URL='https://www.pap.fr'

# Defind pap html page
PAP_ADS_HTML_FILE='html/PAP_ADS_0.html'

# Define imgs root
PAP_IMG_ROOT='imgs/pap'

# Set the path to your Chrome WebDriver
webdriver_path = 'D:\\tools\\chromedriver_win32\\chromedriver.exe'

# Define reference data path
PAP_APPT_ON_SALE_CSV = 'src/pap_appt_on_sale.csv'

# Container Class that stores an ad's values
class AdContainer(object):
    def __init__(self, city, post_code, piece, badrooms, price,surface,link, desc):

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("AdContainer")

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

    def toString(self):
        return "City: " + str(self.city) + "\tpost_code: " + str(self.post_code) + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) + "\tlink: " + str(self.link)

    def to_tuple(self):
        return (self.city, self.post_code, self.piece,self.badrooms, self.link, self.desc)


    def to_csv(self):
        with open(PAP_APPT_ON_SALE_CSV, "a") as stream:
            writer = csv.writer(stream)
            writer.writerow(self.to_tuple())


class AdContainerWithDetail(AdContainer):
    def __init__(self,city, post_code, piece, badrooms, price,surface,link, desc, detail_html):
        super().__init__(city, post_code, piece, badrooms, price,surface,link,desc)

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("AdContainerWithDetail")

        self.detail_html = detail_html

        # init field values
        self.detail=''
        self.monthly_simu = 0
        self.ref=''
        self.updated_at=''
        self.ce = ''
        self.ges = ''
        self.trasports = ''

        # init extra info field
        self.elevator = ''
        self.balcon = ''
        self.cave = ''
        self.parking = ''
        self.floor = ''
        self.warming = ''
        self.window = ''
        self.mngt_fee = ''
        self.ppt_tax = ''
        self.shower = ''
        self.bedroom_desc = ''
        self.livroom_desc = ''
        self.kitchen_desc  = ''


        self.extractInfoFromDetail()
        self.extractExtraInfoFromDetailText()
        self.downloadImages()


    def downloadImages(self):
        page_soup = BeautifulSoup(self.detail_html,features="lxml")
        regex_img_tags = re.compile('owl-thumb-item.*')
        img_parent_tags = page_soup.findAll("a", {"class":regex_img_tags})
        self.log.debug("Found "+str(len(img_parent_tags)))
        index=0
        if img_parent_tags is not None:
            for img_parent_tag in img_parent_tags:
                index += 1
                img_tag = img_parent_tag.find("img")
                img_url = img_tag['src']
                self.log.debug("Downloading img from "+img_url)
                img_path = urlparse(img_url)
                img_name = os.path.basename(img_path.path)
                img_dir = self.ref.replace('/','-')
                file_path = PAP_IMG_ROOT+'/'+img_dir+'/'+img_name
                new_file = file_path.replace('.','-'+str(index)+'.')

                img = Image.open(requests.get(img_url, stream = True).raw)

                isExist = os.path.exists(PAP_IMG_ROOT+'/'+img_dir)
                if not isExist:
                    os.makedirs(PAP_IMG_ROOT+'/'+img_dir)
                img.save(new_file)


    def extractExtraInfoFromDetailText(self):
        html_list=self.detail_tag.get_text(strip=True, separator='\n').splitlines()
        self.log.debug("Detail text: "+self.detail_tag.get_text(strip=True, separator='\n'))
        text_list = []
        for html_ele in html_list:
            #list_one_line = re.split(';|,|.', html_ele)
            list_one_line = html_ele
            text_list += list_one_line


        for line in self.detail_tag.get_text(strip=True, separator='\n'):
            line=line.strip()
            #self.log.debug('Analyzing detail line: '+line)
            if 'ascenseur'.lower() in line.lower():
                self.elevator += line.strip()
            if 'balcon'.lower() in line.lower() or 'terasse' in line:
                self.balcon += line.strip()
            if 'cave'.lower() in line.lower():
                self.cave += line.strip()
            if 'parking'.lower() in line.lower():
                self.parking += line.strip()
            if 'étage'.lower() in line.lower():
                self.floor += line.strip()
            if 'chauffage'.lower() in line.lower():
                self.warming += line.strip()
            if 'fenetre'.lower() in line.lower():
                self.window += line.strip()
            if 'charge'.lower() in line.lower():
                self.mngt_fee += line.strip()
            if 'salle de Bain'.lower() in line.lower() or 'douch'.lower() in line.lower():
                self.shower += line.strip()
            if 'chambre'.lower() in line.lower():
                self.bedroom_desc += line.strip()
            if 'séjour'.lower() in line.lower():
                self.livroom_desc += line.strip()+'.'
            if 'cuisine'.lower() in line.lower():
                self.kitchen_desc += line.strip()+'. '


    def extractInfoFromDetail(self):
        page_soup = BeautifulSoup(self.detail_html,features="lxml")
        container = page_soup.find("div", {"class":"wrapper"})

        self.detail_tag = page_soup.find("div", {"class":"margin-bottom-30"}).find('p')
        self.detail = self.detail_tag.text.replace('\n', '').replace('\t','').replace('"',"'")

        self.monthly_simu = container.find("span", {"class":"item-mensualite-prix"}).text.replace(' €','').replace(',','')

        ref_date = container.find("p", {"class":"item-date"}).text
        if ref_date is not None:
            ref_date_list = ref_date.split("/")
            self.ref = ref_date_list[0].replace("Réf. : ","").replace('\t','').replace('\n','')+"/"+ref_date_list[1]
            self.ref = self.ref.replace(' ','')
            self.updated_at = ref_date_list[2].replace('\t','').strip()

        if container.findAll("div", {"class":"energy-indice"}) is not None:
            if container.find("div", {"class":"energy-indice"}) is not None:
                    self.ce = container.find("div", {"class":"energy-indice"}).find("li", {"class":"active"}).text
        if container.findAll("div", {"class":"ges-indice"}) is not None:
            if container.find("div", {"class":"ges-indice"}) is not None:
                    self.ges = container.find("div", {"class":"ges-indice"}).find("li", {"class":"active"}).text

        if container.findAll("ul", {"class":"item-transports"}) is not None:
            transport_tags = container.findAll("ul", {"class":"item-transports"})
            for transport_tag in transport_tags:
                transport_label = transport_tag.find("span", {"class":"label"}).text+':'
                self.transports = transport_label
                regex_transport_lines = re.compile('icon .*')
                transport_lines = transport_tag.findAll("span", {"class":regex_transport_lines})
                for line_tag in transport_lines:
                    self.transports += line_tag['class'][0]+','
                self.transports +=';'

    def dump(self):
        print("City: " + str(self.city) + "\tpost_code: " + str(self.post_code) + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) + "\tlink: " + str(self.link)  + " detail: " + str(self.detail) + " monthly_simu : " + str(self.monthly_simu) + " ref: " + str(self.ref) + " updated_at: " + str(self.updated_at) + " ce : " + str(self.ce) + " ges : " + str(self.ges) + " trasports : " + str(self.trasports) + " elevator : " + str(self.elevator) + " balcon : " + str(self.balcon) + " cave : " + str(self.cave) + " parking : " + str(self.parking) + " floor : " + str(self.floor) + " warming : " + str(self.warming) + " window : " + str(self.window) + " mngt_fee : " + str(self.mngt_fee) + " ppt_tax : " + str(self.ppt_tax) + " shower : " + str(self.shower) + " bedroom_desc : " + str(self.bedroom_desc) + " livroom_desc : " + str(self.livroom_desc) + " kitchen_desc : " + str(self.kitchen_desc))

    def toString(self):
        return "city: " + str(self.city) + "\tpost_code: " + str(self.post_code) \
        + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) \
        + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) \
        + "\tlink: " + str(self.link) + "\tdetail: " + str(self.detail) \
        + "\tmonthly_simu : " + str(self.monthly_simu) + "\tref: " + str(self.ref) \
        + "\tupdated_at: " + str(self.updated_at) + "\tce : " + str(self.ce) \
        + "\tges : " + str(self.ges) + "\ttrasports : " + str(self.trasports) \
        + "\televator : " + str(self.elevator) + "\tbalcon : " + str(self.balcon) \
        + "\tcave : " + str(self.cave) + "\tparking : " + str(self.parking) \
        + "\tfloor : " + str(self.floor) + "\twarming : " + str(self.warming) \
        + "\twindow : " + str(self.window) + "\tmngt_fee : " + str(self.mngt_fee) \
        + "\tppt_tax : " + str(self.ppt_tax) + "\tshower : " + str(self.shower) \
        + "\tbedroom_desc : " + str(self.bedroom_desc) + "\tlivroom_desc : "+ str(self.livroom_desc) \
        + "\tkitchen_desc : " + str(self.kitchen_desc)

    def to_tuple(self):
        return (self.city, self.post_code, self.piece, self.badrooms, self.link, self.desc, \
            self.detail, self.monthly_simu, self.ref, self.updated_at, self.ce, self.ges, \
            self.trasports, self.elevator, self.balcon, self.cave, self.parking, self.floor, \
            self.warming, self.window, self.mngt_fee, self.ppt_tax, self.shower, \
            self.bedroom_desc, self.livroom_desc, self.kitchen_desc)


    def to_csv(self):
        with open(PAP_APPT_ON_SALE_CSV, "a") as stream:
            writer = csv.writer(stream)
            writer.writerow(self.to_tuple())



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

    def scrap_summary_html(self):

        # Load the page with JavaScript and cookies requirement
        self.driver.get(PAP_URL)

        # Continue without accepting cookie
        cookie_deny = self.driver.find_element(By.CLASS_NAME, "sd-cmp-3ScGE")
        cookie_deny.click()

        # Save html content to file
        with open(PAP_ADS_HTML_FILE, "w", encoding='utf-8') as f:
            f.write(self.driver.page_source)

        # parse ads
        html = self.driver.page_source
        return html

    def scrap_detail_html(self,link):
        print(PAP_BASE_URL+link)
        url=PAP_BASE_URL+link
        url=url.replace('www.pap.frhttps','')

        if PAP_BASE_URL in url:
            self.driver.get(url)

            self.log.debug("Collecting detail page from "+url)
            html = self.driver.page_source
            return html
        return None

    def getPageHtmlFromFile(self):
        with open(PAP_ADS_HTML_FILE, 'r') as file:
            data = file.read()
            return data
        return None

    def parseAds(self,html):
        page_soup = BeautifulSoup(html,features="lxml")
        ads = []

        #print(page_soup)
        containers = page_soup.find("div", {"class":"row row-large-gutters page-item"}).findAll("div", {"class":"search-list-item-alt"})
        self.log.debug("To collect "+str(len(containers))+ " ads on the current page.")

        for container in containers:

            #print(container)
            city = ""
            post_code = 0
            badrooms=0
            piece=0
            surface=0

            price = container.findAll("span", {"class":"item-price"})

            # determin if container is a real ad
            if ("€" in price[0].text ):
                # city + post code in title
                city_pc = container.find("a", {"class":"item-title"}).find("span", {"class":"h1"}).text
                # city name
                city = city_pc.split("(")[0].strip()

                if len(city_pc.split("(")) >1:
                    # post code
                    post_code = city_pc.split("(")[1].split(")")[0].strip()

                # get other info
                tags_parent = container.findAll("ul", {"class":"item-tags"})

                if len(tags_parent) >0 :
                    tags = tags_parent[0].findAll("li")
                    for tag in tags:
                        if ( " pièces" in tag.text ):
                            piece = tag.text.replace(' pièces','')
                        elif ( " chambre" in tag.text):
                            badrooms = tag.text.replace(' chambre','')
                        elif ( " m2" in tag.text ):
                            surface = tag.text.replace(' m2','')

                price = container.find("span", {"class":"item-price"}).text.split('(')[0].strip().replace('€','').replace('.','')
                link = container.find("a", {"class":"item-title"})['href']
                desc = container.find("p", {"class":"item-description"}).text.replace('\n', '').replace('"',"'")

                # get detail html of one ad
                detail_html = self.scrap_detail_html(link)
                if detail_html is not None:
                    adContainer = AdContainerWithDetail(city, post_code, piece, badrooms, price,surface,link, desc, detail_html)

                    self.log.debug("Extract "+ adContainer.toString())
                    adContainer.to_csv()
                    ads.append(adContainer)

            # sleep 5 seconds before collecting each ad page
            time.sleep(5)

        return ads

if __name__ == "__main__":
    papScrapper = PAPScrapper()
    html=papScrapper.scrap_summary_html()
    #html=papScrapper.getPageHtmlFromFile(
    papScrapper.parseAds(html)
