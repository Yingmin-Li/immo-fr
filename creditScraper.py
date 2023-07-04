from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time
import json
import pandas as pd

from setupLogger import ScrapLogger


CREDIT_SIMU_URL='https://www.lafinancepourtous.com/outils/calculateurs/calculateur-de-credit-immobilier/'

CREDIT_MONTH_20_YEARS = 20 * 12
CREDIT_MONTH_25_YEARS = 25 * 12

CREDIT_RATE_20_YEARS = '2,55'
CREDIT_RATE_25_YEARS = '2,67'

# Set the path to your Chrome WebDriver
webdriver_path = 'D:\\tools\\chromedriver_win32\\chromedriver.exe'

# Define reference data path
PAP_APPT_ON_SALE_CSV = 'src/pap_appt_on_sale.csv'
PAP_APPT_ON_SALE_WITH_CREDIT_CSV = 'src/pap_appt_on_sale_with_credit.csv'

# Container Class that stores an ad's values
class CreditScraper(object):

    def __init__(self):

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("CreditScraper")

        # Configure Chrome options
        self.chrome_options = Options()
        self.userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
        self.chrome_options.add_argument(f'user-agent={self.userAgent},referer={CREDIT_SIMU_URL}')

        # Create a new Chrome driver instance
        self.service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def search_credits_per_month(self,capital):

        self.log.info("Searching credits for "+str(capital))

        # Load the page with JavaScript and cookies requirement
        self.driver.get(CREDIT_SIMU_URL)

        # search credit per month of 20 years
        func_tag = self.driver.find_element(By.ID, "rech")
        select_func_tag = Select(func_tag)
        select_func_tag.select_by_visible_text('Calculer la mensualité')

        capital_tag = self.driver.find_element(By.ID, "capital")
        self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])",capital_tag, capital)
        capital_tag.send_keys(capital)

        rate_tag = self.driver.find_element(By.ID, "taux")
        self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])",rate_tag, CREDIT_RATE_20_YEARS)
        rate_tag.send_keys(CREDIT_RATE_20_YEARS)

        period_tag = self.driver.find_element(By.ID, "duree")
        self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])",period_tag, CREDIT_MONTH_20_YEARS)
        period_tag.send_keys(CREDIT_MONTH_20_YEARS)

        request_box = self.driver.find_element(By.ID, "calculateur")
        #print(request_box.text)

        request_box.submit()
        #javas = "document.getElementsById('calculateur')[0].submit();"
        #javas = "document.calculateur.submit();"
        #self.driver.execute_script(javas)

        #time.sleep(1)

        credit_per_month_20Y = self.driver.find_element(By.ID,"echeance").get_attribute('value').replace(' ','')
        credit_cost_20Y = self.driver.find_element(By.ID,"cout").get_attribute('value').replace(' ','')

        self.log.info("Found credit_per_month_20Y:" + str(credit_per_month_20Y))
        self.log.info("Found credit_cost_20Y:" + str(credit_cost_20Y))

        # search credit per month of 25 years
        func_tag = self.driver.find_element(By.ID, "rech")
        select_func_tag = Select(func_tag)
        select_func_tag.select_by_visible_text('Calculer la mensualité')

        #capital_tag = self.driver.find_element(By.ID, "capital")
        #self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])",capital_tag, capital)
        #capital_tag.send_keys(capital)

        rate_tag = self.driver.find_element(By.ID, "taux")
        self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])",rate_tag, CREDIT_RATE_25_YEARS)
        rate_tag.send_keys(CREDIT_RATE_25_YEARS)

        period_tag = self.driver.find_element(By.ID, "duree")
        self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])",period_tag, CREDIT_MONTH_25_YEARS)
        period_tag.send_keys(CREDIT_MONTH_25_YEARS)

        request_box = self.driver.find_element(By.ID, "calculateur")
        request_box.submit()

        credit_per_month_25Y = self.driver.find_element(By.ID,"echeance").get_attribute('value').replace(' ','')
        credit_cost_25Y = self.driver.find_element(By.ID,"cout").get_attribute('value').replace(' ','')

        self.log.info("Found credit_per_month_25Y:" + str(credit_per_month_25Y))
        self.log.info("Found credit_cost_25Y:" + str(credit_cost_25Y))

        return credit_per_month_20Y, credit_cost_20Y, credit_per_month_25Y, credit_cost_25Y


    def search_credits(self, path_to_csv, price_col_name):

        # Load the page with JavaScript and cookies requirement
        self.driver.get(CREDIT_SIMU_URL)

        html=self.driver.page_source
        time.sleep(1)
        #print(html)

        # Continue without accepting cookie
        cookie_deny = self.driver.find_element(By.XPATH,'//*[@id="tarteaucitronAlertBig"]/button[3]')
        print(cookie_deny.text)
        cookie_deny.click()

        # Setup rent info pd
        appt_on_sale_pd=pd.read_csv(path_to_csv, sep=',')
        appt_on_sale_pd['credit_per_month_20Y'], appt_on_sale_pd['credit_cost_20Y'], appt_on_sale_pd['credit_per_month_25Y'], appt_on_sale_pd['credit_cost_25Y'] = zip(*appt_on_sale_pd[price_col_name].apply(self.search_credits_per_month))

        # Write df to CSV
        appt_on_sale_pd.to_csv(PAP_APPT_ON_SALE_WITH_CREDIT_CSV, mode='a',header=False,index=False)

if __name__ == "__main__":
    creditScraper = CreditScraper()
    creditScraper.search_credits(PAP_APPT_ON_SALE_CSV,'price')
