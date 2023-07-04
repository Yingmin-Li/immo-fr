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

# Download image
DOWNLOAD_IMG=True

# Page limit
PAGE_LIMIT=200

# Define urls
SELOGER_URL='https://www.seloger.com/list.htm?projects=2,5&types=1&natures=1,2,4&places=[{%22subDivisions%22:[%2292%22]},{%22subDivisions%22:[%2294%22]},{%22subDivisions%22:[%2275%22]}]&price=150000/330000&surface=30/50&bedrooms=1&rooms=2&mandatorycommodities=0&enterprise=0&qsVersion=1.0&m=search_refine-redirection-search_results'
SELOGER_BASE_URL='https://www.seloger.fr'
SELOGER_STATIS_BASE_URL='https://v.seloger.com'
SELOGER_CDN_BASE_URL='https://cdn.seloger.com'
SELOGER_UPLOAD_BASE_URL='https://upload.seloger.com'

# Defind seloger html page
SELOGER_ADS_HTML_FILE='html/SELOGER_ADS_0.html'

# Define imgs root
SELOGER_IMG_ROOT='imgs/seloger'

# Set the path to your Chrome WebDriver
webdriver_path = 'D:\\tools\\chromedriver_win32\\chromedriver.exe'

# Define reference data path
SELOGER_APPT_ON_SALE_CSV = 'src/SELOGER_appt_on_sale.csv'

# Container Class that stores an ad's values
class AdContainer(object):
    def __init__(self, city, post_code, piece, badrooms, price,surface,link, desc):

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("AdContainer")

        self.city = city
        self.post_code = post_code
        self.insee_code = insee_code
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
        with open(SELOGER_APPT_ON_SALE_CSV, "a") as stream:
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
        self.transports = ''
        self.contact = ''


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
        if DOWNLOAD_IMG:
            self.downloadImages()


    def downloadImages(self):
        page_soup = BeautifulSoup(self.detail_html,features="lxml")
        regex_img_tags = re.compile('owl-thumb-item.*')
        img_parent_tags = page_soup.findAll("a", {"class":regex_img_tags})
        self.log.debug("Found "+str(len(img_parent_tags))+" images")
        index=0
        if img_parent_tags is not None:
            for img_parent_tag in img_parent_tags:
                index += 1
                img_tag = img_parent_tag.find("img")
                img_url = img_tag['src']
                if not SELOGER_BASE_URL in img_url and not SELOGER_STATIS_BASE_URL in img_url and not SELOGER_CDN_BASE_URL in img_url and not SELOGER_UPLOAD_BASE_URL in img_url:
                    img_url =SELOGER_BASE_URL+img_url
                self.log.info("Downloading img from "+img_url)
                img_path = urlparse(img_url)
                img_name = os.path.basename(img_path.path)
                img_dir = self.ref.replace('/','-')
                file_path = SELOGER_IMG_ROOT+'/'+img_dir+'/'+img_name
                new_file = file_path.replace('.','-'+str(index)+'.')

                img = Image.open(requests.get(img_url, stream = True).raw)

                isExist = os.path.exists(SELOGER_IMG_ROOT+'/'+img_dir)
                if not isExist:
                    os.makedirs(SELOGER_IMG_ROOT+'/'+img_dir)
                img.save(new_file)


    def extractExtraInfoFromDetailText(self):
        html_list=self.detail_tag.get_text(strip=True, separator='\n').splitlines()
        text_list = []
        for html_ele in html_list:
            #list_one_line = re.split(';|,|.', html_ele)
            list_one_line = html_ele
            text_list += list_one_line


        for line in re.split(';|\.', self.detail_tag.text):
            line=line.strip().replace('\n','').replace(',','').replace('"','')
            self.log.debug('Analyzing detail line: '+line)
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
            self.log.debug("Transport tags: "+ str(transport_tags[0].attrs))
            for transport_tag in transport_tags:
                transport_label_tag = transport_tag.find("span", {"class":"label"})
                if transport_label_tag is not None:
                    transport_label = transport_label_tag.text+':'
                    self.transports = transport_label
                    regex_transport_lines = re.compile('icon .*')
                    transport_lines = transport_tag.findAll("span", {"class":regex_transport_lines})
                    for line_tag in transport_lines:
                        self.transports += line_tag['class'][1]+','
                    self.transports +=';'
                    self.log.debug("All transport tags : "+ self.transports)
        if container.find("p", {"class":"h3 txt-indigo"}) is not None:
            self.contact = container.find("p", {"class":"h3 txt-indigo"}).text.replace(" ",'').replace("\.",'').replace("\t",'').replace("\n",'')

    def dump(self):
        print("City: " + str(self.city) + "\tpost_code: " + str(self.post_code) + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) + "\tlink: " + str(self.link)  + " detail: " + str(self.detail) + " monthly_simu : " + str(self.monthly_simu) + " ref: " + str(self.ref) + " updated_at: " + str(self.updated_at) + " ce : " + str(self.ce) + " ges : " + str(self.ges) + " transports : " + str(self.transports)+ " contact : " + str(self.contact) + " elevator : " + str(self.elevator) + " balcon : " + str(self.balcon) + " cave : " + str(self.cave) + " parking : " + str(self.parking) + " floor : " + str(self.floor) + " warming : " + str(self.warming) + " window : " + str(self.window) + " mngt_fee : " + str(self.mngt_fee) + " ppt_tax : " + str(self.ppt_tax) + " shower : " + str(self.shower) + " bedroom_desc : " + str(self.bedroom_desc) + " livroom_desc : " + str(self.livroom_desc) + " kitchen_desc : " + str(self.kitchen_desc))

    def toString(self):
        return "city: " + str(self.city) + "\tpost_code: " + str(self.post_code) \
        + "\tpiece: " + str(self.piece) + "\tbadrooms: " + str(self.badrooms) \
        + "\tprice: " + str(self.price)  + "\tsize: " + str(self.size) \
        + "\tlink: " + str(self.link) + "\tdetail: " + str(self.detail) \
        + "\tmonthly_simu : " + str(self.monthly_simu) + "\tref: " + str(self.ref) \
        + "\tupdated_at: " + str(self.updated_at) + "\tce : " + str(self.ce) \
        + "\tges : " + str(self.ges) + "\ttransports : " + str(self.transports) \
        + "\tcontact : " + str(self.contact) \
        + "\televator : " + str(self.elevator) + "\tbalcon : " + str(self.balcon) \
        + "\tcave : " + str(self.cave) + "\tparking : " + str(self.parking) \
        + "\tfloor : " + str(self.floor) + "\twarming : " + str(self.warming) \
        + "\twindow : " + str(self.window) + "\tmngt_fee : " + str(self.mngt_fee) \
        + "\tppt_tax : " + str(self.ppt_tax) + "\tshower : " + str(self.shower) \
        + "\tbedroom_desc : " + str(self.bedroom_desc) + "\tlivroom_desc : "+ str(self.livroom_desc) \
        + "\tkitchen_desc : " + str(self.kitchen_desc)

    def to_tuple(self):
        return (self.city, self.post_code, self.piece, self.badrooms, \
            self.price, self.size,self.link, self.desc, \
            self.detail, self.monthly_simu, self.ref, self.updated_at, self.ce, self.ges, \
            self.transports,self.contact, self.elevator, self.balcon, self.cave, self.parking,\
            self.floor, self.warming, self.window, self.mngt_fee, self.ppt_tax, self.shower, \
            self.bedroom_desc, self.livroom_desc, self.kitchen_desc)


    def to_csv(self):
        with open(SELOGER_APPT_ON_SALE_CSV, "a", newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(self.to_tuple())



class SelogerScrapper():

    def __init__(self):
        super().__init__()

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("SelogerScrapper")

        # Configure Chrome options
        self.chrome_options = Options()
        self.userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
        self.chrome_options.add_argument(f'user-agent={self.userAgent},referer={SELOGER_URL}')

        # Create a new Chrome driver instance
        self.service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def getPageSoupFromFile(path):
        file = open(path, "r")
        r = file.read()
        return (soup(r, "html.parser"))

    def scrap_one_summary_html(self,url,check_cookie=False):

        # Load the page with JavaScript and cookies requirement
        self.driver.get(url)

        # Continue without accepting cookie
        if check_cookie:
            cookie_deny = self.driver.find_element(By.CLASS_NAME, "didomi-continue-without-agreeing")
            cookie_deny.click()

        # Save html content to file
        with open(SELOGER_ADS_HTML_FILE, "w", encoding='utf-8') as f:
            f.write(self.driver.page_source)

        # parse ads
        html = self.driver.page_source
        return html

    def scrap_all_summary(self):
        html=self.scrap_one_summary_html(SELOGER_URL,True)
        self.parseAdsPnOnePage(html)

        for i in range(2,PAGE_LIMIT):
            url=SELOGER_URL+'-'+str(i)
            self.log.info("Collecting from "+url)
            html=self.scrap_one_summary_html(url)
            self.parseAdsPnOnePage(html)

    def scrap_detail_html(self,link):
        print(SELOGER_BASE_URL+link)
        url=SELOGER_BASE_URL+link
        url=url.replace('www.seloger.comhttps','')

        if SELOGER_BASE_URL in url:
            self.driver.get(url)

            self.log.debug("Collecting detail page from "+url)
            html = self.driver.page_source
            return html
        return None

    def getPageHtmlFromFile(self):
        with open(SELOGER_ADS_HTML_FILE, 'r') as file:
            data = file.read()
            return data
        return None

    def parseAdsPnOnePage(self,html):
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

                price = container.find("span", {"class":"item-price"}).text.split('(')[0].strip().replace('€','').replace('.','').replace(' ','')
                link = container.find("a", {"class":"item-title"})['href']
                desc = container.find("p", {"class":"item-description"}).text.replace('\n', '').replace('\t', '').replace('"',"'")

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
    selogerScrapper = SelogerScrapper()
    selogerScrapper.scrap_all_summary()


