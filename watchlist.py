from bs4 import BeautifulSoup
import requests
from datetime import datetime

# scrapes stock news from finviz
def screener():
    #Fundamental screener on finviz
    url_fu = 'https://finviz.com/screener.ashx?v=411&f=fa_debteq_u0.7,fa_epsqoq_pos,fa_ltdebteq_u0.7,fa_quickratio_o1,fa_salesqoq_pos,ind_stocksonly,sh_curvol_o100,sh_price_u2,ta_rsi_nob60,ta_sma20_pa&ft=3'
    html_fu = requests.get(url_fu, headers={'User-Agent': 'Mozilla/5.0'})
    soup_fu = BeautifulSoup(html_fu.text, 'lxml')
    
    # finds ticker table within finviz website
    match_fu = soup_fu.find('table', width="100%", cellpadding="10")
    
    fu_tickers = []
    
    if match_fu  != None:
        for t in match_fu.find_all('span'):
            temp = str(t.text)
            temp2 = temp.strip('\xa0')
            fu_tickers.append(temp2)
    else:
        fu_tickers.append('Check back after hours')
     
    # TA screener on finviz    
    url_ta = 'https://finviz.com/screener.ashx?v=411&f=cap_microunder,sh_curvol_o200,sh_float_u100,sh_price_u2,sh_relvol_o3,ta_perf_dup,ta_sma20_pa&ft=4'
    html_ta = requests.get(url_ta, headers={'User-Agent': 'Mozilla/5.0'})
    soup_ta = BeautifulSoup(html_ta.text, 'lxml')
    
    # finds ticker table within finviz website
    match_ta = soup_ta.find('table', width="100%", cellpadding="10")
    
    ta_tickers = []
    
    if match_ta != None:
        for t in match_ta.find_all('span'):
            temp = str(t.text)
            temp2 = temp.strip('\xa0')
            ta_tickers.append(temp2)
    else:
        ta_tickers.append('Check back after hours')
    
    #Combines lists without duplicates
    # tickers_final = list(set(fu_tickers + ta_tickers))
    tickers_final = 'Check back after hours'
    date_today = datetime.today().strftime('%Y-%m-%d')

    return tickers_final, date_today

    
