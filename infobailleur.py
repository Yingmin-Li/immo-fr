from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import json
import pandas as pd

from setupLogger import ScrapLogger

# Define urls
RENT_URL='https://www.locservice.fr/cote-des-loyers/evaluation-cote-f2-infobailleur.html'
PC_URL_BASE = "https://www.locservice.fr/services/villes_geo.json?Metropoles=0&SearchField="

# Define reference data path
GEO_INFO_INSEE_CSV = 'src/geo_info_insee.csv'
RENT_INFO_CSV = 'src/rent_info.csv'



class InfoBailleur():

    def __init__(self,driver):
        super().__init__()

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("InfoBailleur")

        self.driver = driver


    def search_geo_info_insee(self, post_code,insee_code):
        # Get code by post code
        pc_url = PC_URL_BASE+post_code
        self.driver.get(pc_url)
        html = driver.page_source
        time.sleep(2)
        #print(driver.find_element(By.TAG_NAME,'body').text)

        json_object = json.loads(driver.find_element(By.TAG_NAME,'body').text)

        insee_code = json_object[0]['value']
        city_label = json_object[0]['label']

        #print(insee_code)
        #print(city_label)

        #json_formatted_str = json.dumps(json_object, indent=2)
        #print(json_formatted_str)

        return post_code,insee_code,city_label

    def get_geo_info_insee(self, post_code,insee_code):
        # Setup geo info insee pd
        insee_pd=pd.read_csv(GEO_INFO_INSEE_CSV, sep=';')
        #self.log.debug("get_geo_info_insee has "+ ','.join(map(str,insee_pd['post_code'].values)))
        if post_code not in insee_pd['post_code'].values:
            post_code,insee_code,city_label = self.search_geo_info_insee(post_code,insee_code)
            if post_code is not None:
                self.log.debug("Found "+str(post_code)+" "+ str(insee_code)+" "+ str(city_label)+str(GEO_INFO_INSEE_CSV))
                return post_code,insee_code,city_label
        else:
            res = insee_pd.query('post_code == '+ str(post_code) + ' & insee_code== '+ str(insee_code))
            self.log.debug("Found insee info from reference "+','.join(map(str, res.values.flatten().tolist())))
            post_code,insee_code,city_label = res['post_code'].item(), res['insee_code'].item(),res['city_label'].item()
            return post_code,insee_code,city_label

        return None,None,None

    def search_rent(self,post_code,insee_code,city_label):

        # Load the page with JavaScript and cookies requirement
        self.driver.get(RENT_URL)

        #html = driver.page_source
        #time.sleep(2)
        #print(html)

        # Decline all cookies
        #cookie_deny = driver.find_element("id", "ppms_cm_reject-all")
        #cookie_deny.click()

        city = self.driver.find_element(By.ID, "uiVille")
        city.send_keys(city_label)

        logement = self.driver.find_element(By.ID, "Logement")
        select_logment = Select(logement)
        select_logment.select_by_visible_text('T2')

        insee = self.driver.find_element(By.ID, "Insee")

        print("insee_code is: "+str(insee_code))
        self.driver.execute_script("arguments[0].value='"+str(insee_code)+"';",insee)

        format_v = self.driver.find_element(By.ID, "Format")
        self.driver.execute_script("arguments[0].value='2';",format_v)

        request_box = self.driver.find_element(By.NAME, "Form0")
        javas = "document.Form0.submit();"
        self.driver.execute_script(javas)
        #request_box.submit()

        tbl = self.driver.find_element(By.XPATH,"/html/body/div[2]/table").get_attribute('outerHTML')

        # returned a list of df
        df  = pd.read_html(tbl)
        df = df[0]
        del df[df.columns[0]]

        df['post_code'] = post_code
        df['insee_code'] = insee_code
        df['city_label'] = city_label
        df['surface_class'] = df.index
        df['surface_class'] += 1
        # set surface_class as the first column
        first_column = df.pop('surface_class')
        df.insert(0, 'surface_class', first_column)

        # get avg rent from html
        avg_rent_1=None
        avg_rent_2=None
        avg_rent_3=None

        col_num=len(WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[2]/table/tbody/tr[1]/td"))))
        self.log.debug("Rent table class 1, col_num="+str(col_num))
        if col_num == 4:
            avg_rent_1=self.driver.find_element(By.XPATH,"/html/body/div[2]/table/tbody/tr[1]/td[3]").text

        col_num=len(WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[2]/table/tbody/tr[2]/td"))))
        self.log.debug("Rent table class 3, col_num="+str(col_num))
        if col_num == 4:
            avg_rent_2=self.driver.find_element(By.XPATH,"/html/body/div[2]/table/tbody/tr[2]/td[3]").text

        col_num=len(WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[2]/table/tbody/tr[3]/td"))))
        self.log.debug("Rent table class 3, col_num="+str(col_num))
        if col_num == 4:
            avg_rent_3=self.driver.find_element(By.XPATH,"/html/body/div[2]/table/tbody/tr[3]/td[3]").text

        df['Loyer Moyen'][0]=avg_rent_1
        df['Loyer Moyen'][1]=avg_rent_2
        df['Loyer Moyen'][2]=avg_rent_3

        #df.drop(['surface'], axis=1)
        df = df.replace(['Pas assez de loyer de référence'], None)
        df = df.replace(' €','', regex=True)
        df.replace('\.','', regex=True,inplace=True)
        df = df.replace('NAN','', regex=True)

        #df = df['Loyer Mini'].replace(' ','', regex=True)
        #df = df['Loyer Moyen'].replace(' ','', regex=True)
        #df = df['Loyer Maxi'].replace(' ','', regex=True)


        res = df.query('post_code == '+ str(post_code) + ' & surface_class==2 ')
        self.log.debug("Search-rent found "+','.join(map(str, res.values.flatten().tolist())))

        df.to_csv(RENT_INFO_CSV, mode='a',header=False,index=False)

        return res['surface_class'].item(), \
        res['Loyer Mini'].item(), \
        res['Loyer Moyen'].item(), \
        res['Loyer Maxi'].item()

    def get_rent_range_by_post_code(self, post_code,insee_code):

        # Get geo insee info
        (post_code1, insee_code1, city_label)= self.get_geo_info_insee(post_code,insee_code)

        # Setup rent info pd
        rent_pd=pd.read_csv(RENT_INFO_CSV, sep=',')

        if post_code not in rent_pd['post_code'].values or insee_code not in rent_pd['insee_code'].values:
            surface_class,rent_min,rent_avg,rent_max = self.search_rent(post_code,insee_code, city_label)
            if post_code is not None:
                self.log.debug("Found "+str(surface_class)+', '+str(rent_min)+', '+str(rent_avg)+', '+str(rent_max)+', '+str(post_code) + " from refence file "+str(RENT_INFO_CSV))
                return surface_class,rent_min,rent_avg,rent_max,post_code,insee_code,city_label
        else:
            #res = rent_pd[(rent_pd['post_code'] == post_code) & (rent_pd['surface_class'] == 2)]
            print(insee_code1)
            print(insee_code)
            res = rent_pd.query('post_code == '+ str(post_code)+'& insee_code == '+ str(insee_code) + ' & surface_class==2 ')

            self.log.debug("Found rent info from remote site "+','.join(map(str, res.values.flatten().tolist())))
            surface_class,rent_min,rent_avg,rent_max,post_code,insee_code,city_label = \
            res['surface_class'].item() if res is not None else None, \
            res['rent_min'].item() if res['rent_min'] is not None else None, \
            res['rent_avg'].item() if res['rent_avg'] is not None else None, \
            res['rent_max'].item() if res['rent_max'] is not None else None,\
            res['post_code'].item(), res['insee_code'].item(),res['city_label'].item()
            return surface_class,rent_min,rent_avg,rent_max,post_code,insee_code,city_label

        return None,None,None,None,None,None,None


