import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infobailleur import InfoBailleur
from setupLogger import ScrapLogger

# Define url
RENT_URL='https://www.locservice.fr/cote-des-loyers/evaluation-cote-f2-infobailleur.html'

# Define reference data path
GEO_INFO_INSEE_CSV = 'src/geo_info_insee.csv'

# Set the path to your Chrome WebDriver
webdriver_path = 'D:\\tools\\chromedriver_win32\\chromedriver.exe'

class ImmoSrapper(object):
    def __init__(self):
        # Setup logger
        immoScrapperLogger = ScrapLogger()
        self.log = immoScrapperLogger.get_logger("ImmoSrapper")

        self.post_codes=post_codes

        # Configure Chrome options
        self.chrome_options = Options()
        self.userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
        self.chrome_options.add_argument(f'user-agent={self.userAgent},referer={RENT_URL}')

        # Create a new Chrome driver instance
        self.service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)


    def scrapAll(self, df, start_post_code, start_insee_code):
        # Collect rent range
        self.infobailleur = InfoBailleur(self.driver)
        l = df.index[ (df['post_code'] == start_post_code) & (df['insee_code'] == start_insee_code)].tolist()
        if l is not None and len(l)>0:
            start_index = l[0]
        else:
            start_index = 0

        self.log.debug("start_index=" +str(start_index))

        #reduced_df = df.loc[[e for lst in [range(idx, idx + len(df)-start_index+1) for idx in
        #     start_index] for e in lst]].copy()
        #reduced_df = reduced_df.reset_index(drop=True)


        reduced_df = df
        #reduced_df = df.iloc[start_index:].tail(10)
        print(reduced_df.head(10))

        for index, row in reduced_df.iterrows():
            self.log.debug("Scrapping "+ str(row['post_code'])+" - "+str(row['insee_code']))
            self.infobailleur.get_rent_range_by_post_code(row['post_code'],row['insee_code'])
            time.sleep(5)

        # After finishing, close the browser
        self.driver.quit()


if __name__ == "__main__":
    insee_pd=pd.read_csv(GEO_INFO_INSEE_CSV, sep=';')
    res=insee_pd[['post_code','insee_code']]

    post_codes=res.values.flatten().tolist()

    start_post_code = 75010
    start_insee_code = 75110

    immoSrapper = ImmoSrapper()
    immoSrapper.scrapAll(res, start_post_code, start_insee_code)

