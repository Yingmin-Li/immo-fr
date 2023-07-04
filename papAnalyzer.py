import time
import json
import pandas as pd
import numpy as np

from setupLogger import ScrapLogger

# input
PAP_APPT_ON_SALE_WITH_CREDIT_CSV = 'src/pap_appt_on_sale_with_credit.csv'
GEO_INFO_INSEE_CSV = 'src/geo_info_insee.csv'
RENT_INFO_CSV = 'src/rent_info.csv'

MIN_SIZE = 30
MAX_SIZE = 50
IDEAL_RENT_SCALE = 1.15
DEFAULT_MGNT_FEE = 200

# output
ANALYZED_PAP_CSV = 'output/analyzed_pap.csv'

class PapAnalyzer(object):

    def __init__(self):

        # Setup logger
        infobailleurLogger = ScrapLogger()
        self.log = infobailleurLogger.get_logger("PapAnalyzer")


    def investible_ideal(self, rent_min, rent_max, rent_avg, size):

        if rent_min == 0:
            rent_min = 0.00001
        if rent_max == 0:
            rent_mam = 0.00001
        if rent_avg == 0:
            rent_avg = 0.00001

        rent_slope = (rent_max - rent_min )/(MAX_SIZE - MIN_SIZE)
        theory_rent = rent_min + (size - MIN_SIZE) * rent_slope
        adjusted_rent = ( theory_rent + rent_avg ) / 2
        ideal_rent = adjusted_rent * IDEAL_RENT_SCALE

        return rent_slope, theory_rent, adjusted_rent, ideal_rent


    def analyze(self):
        # load input files
        appt_pd=pd.read_csv(PAP_APPT_ON_SALE_WITH_CREDIT_CSV, sep=',')
        # cleanse data
        appt_pd['city'].replace('+ Terrasse 8 M² Courbevoie', 'Courbevoie', inplace=True)
        appt_pd['city']=appt_pd['city'].str.casefold()
        #appt_pd.drop_duplicates(keep="last", inplace=True)

        # Write df to CSV
        appt_pd.to_csv('output/appt.csv', mode='w',header=True,index=False)

        geo_pd=pd.read_csv(GEO_INFO_INSEE_CSV, sep=';')
        geo_pd['city_label']=geo_pd['city_label'].str.casefold()

        # Write df to CSV
        geo_pd.to_csv('output/geo.csv', mode='w',header=True,index=False)

        rent_price_pd=pd.read_csv(RENT_INFO_CSV, sep=',').query('surface_class == 2')

        # prepare analysis dataframe
        appt_geo_pd = pd.merge(appt_pd, geo_pd, left_on='city',  right_on='city_label',how='left',suffixes=(None, '_geo'))
        appt_geo_pd['post_code']=appt_geo_pd['post_code_geo']
        appt_geo_pd.sort_values(['post_code', 'link'],
              ascending = [True, True])

        # Write df to CSVs
        appt_geo_pd.to_csv('output/appt_geo.csv', mode='w',header=True,index=False)

        analysis_pd = pd.merge(appt_geo_pd, rent_price_pd, on='insee_code', how='left',suffixes=(None, '_price'))

        # fill missing val in df
        analysis_pd['post_code']=analysis_pd['post_code_geo']
        analysis_pd.drop_duplicates(keep="last", inplace=True)


        # Concert data type
        analysis_pd['post_code'] = analysis_pd['post_code'].fillna(0).astype(int)
        analysis_pd['insee_code'] = analysis_pd['insee_code'].fillna(0).astype(int)
        analysis_pd['price'] = analysis_pd['price'].fillna(0).astype(int)
        analysis_pd['size'] = analysis_pd['size'].fillna(0).astype(float)

        analysis_pd['rent_min'] = analysis_pd['rent_min'].fillna(0).astype(int)
        analysis_pd['rent_max'] = analysis_pd['rent_max'].fillna(0).astype(int)
        analysis_pd['rent_avg'] = analysis_pd['rent_avg'].fillna(0).astype(int)

        # enrich df
        analysis_pd['price_per_sqrt_m'] = analysis_pd['price']/(analysis_pd['size']+0.00000000000001)
        analysis_pd['ideal_rent_price'] = analysis_pd['price']

        # analyse
        analysis_pd['rent_slope'], analysis_pd['theory_rent'], analysis_pd['adjusted_rent'], analysis_pd['ideal_rent'] = zip(*analysis_pd.apply(lambda x: self.investible_ideal(x['rent_min'], x['rent_max'],x['rent_avg'], x['size']), axis=1))

        analysis_pd['investible_20Y'] = np.where(analysis_pd['ideal_rent'] > (analysis_pd['credit_per_month_20Y']+ DEFAULT_MGNT_FEE),True, False)
        analysis_pd['gap_investible_20Y'] = analysis_pd['ideal_rent'] - (analysis_pd['credit_per_month_20Y']+ DEFAULT_MGNT_FEE)


        analysis_pd['investible_25Y'] = np.where(analysis_pd['ideal_rent'] > (analysis_pd['credit_per_month_25Y']+ DEFAULT_MGNT_FEE),True, False)
        analysis_pd['gap_investible_25Y'] = analysis_pd['ideal_rent'] - (analysis_pd['credit_per_month_25Y']+ DEFAULT_MGNT_FEE)

        # Write df to CSV
        analysis_pd.to_csv(ANALYZED_PAP_CSV, mode='w',header=True,index=False)

if __name__ == "__main__":
    papAnalyzer = PapAnalyzer()
    papAnalyzer.analyze()
