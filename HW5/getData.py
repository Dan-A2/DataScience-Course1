import re
import json
import requests
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import jdatetime
jdatetime.set_locale('fa_IR')
from persiantools.jdatetime import JalaliDate


def convert_ar_characters(input_str):

    mapping = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی'
    }
    return _multiple_replace(mapping, input_str)
def _multiple_replace(mapping, text):
    pattern = "|".join(map(re.escape, mapping.keys()))
    return re.sub(pattern, lambda m: mapping[m.group()], str(text))

def get_today_tickers_data():

    url = 'http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?h=0&r=0'
    data = requests.get(url, timeout=12)
    content = data.content.decode('utf-8')
    parts = content.split('@')
    inst_price = parts[2].split(';')
    market_me = {}
    # Add the Trade and other stuff to dataframe--------
    for item in inst_price:
        item=item.split(',')
        market_me[item[0]]= dict(id=item[0],ISIN=item[1],symbol=item[2],
                              name=item[3],first_price=float(item[5]),close_price=float(item[6]),
                              last_trade=float(item[7]),count=item[8],volume=float(item[9]),
                              value=float(item[10]),min_traded_price=float(item[11]),
                              max_treaded_price=float(item[12]),yesterday_price=int(item[13]),
                              table_id=item[17],group_id=item[18],max_allowed_price=float(item[19]),
                              min_allowed_price=float(item[20]),ret_last = (float(item[7]) - float(item[13]))/float(item[13]),
                                 ret_close = (float(item[6]) - float(item[13]))/float(item[13]),
                                number_of_shares=float(item[21]), Market_cap=int(item[21]) *int(item[6]))
    # Add the Ask-Bid price Vol tu dataframe --------
    for item in parts[3].split(';'):
        try:
            item=item.split(',')

            market_me[item[0]]['bid_price{}'.format(item[1])]=  float(item[4])
            market_me[item[0]]['bid_vol{}'.format(item[1])]=  float(item[6])
            
            market_me[item[0]]['ask_price{}'.format(item[1])]=  float(item[5])
            market_me[item[0]]['ask_vol{}'.format(item[1])]=  float(item[7])

        except:
            pass
    df = pd.DataFrame(market_me ).T
    df['name'] = df['name'].apply(convert_ar_characters)
    df = df[df['symbol'].map(lambda x: x.isalpha())]
    df = df[~df['ISIN'].str.startswith('IRT') & ~df['ISIN'].str.startswith('IRR')]
    
    
    return df.reset_index(drop=True)


def get_single_ticker_history(stock_id):
    url = f'http://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={stock_id}&Top=999999&A=0'
    r = requests.get(url)
    content=r.content
    data= content.decode('utf-8').split(';')
    stockinfo={}
    for i in data:
        try:
            eachdayinfo = i.split('@')
            if len(eachdayinfo)==10:
                stockinfo[eachdayinfo[0]] = eachdayinfo[1:]
        except:pass
    df = pd.DataFrame(stockinfo).T
    df.reset_index(inplace=True)
    df.columns= ['date','high','low','close','last','first','yesterday','value','volume','numberoftrades']
    df['date'] = pd.to_datetime(df['date'])
    df[df.columns[1:]] = df[df.columns[1:]].astype(float)
    df["return"] = 1 - df["yesterday"]/df["close"] 
    df.set_index('date' , inplace=True)
    return df
        



def get_today_client_type_tickersData():
    url = 'http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx'
    data = requests.get(url, timeout=15)
    content=data.content.decode('utf-8').split(";")

    clienttype=[]
    for item in content:
        try:
            item=item.split(',')
            clienttype.append(dict( id=item[0],
                                        Individual_buy_count=int(item[1]),
                                            NonIndividual_buy_count=int(item[2]),
                                            Individual_buy_volume=int(item[3]),
                                            NonIndividual_buy_volume=int( item[4]) ,
                                            Individual_sell_count=int(item[5]),
                                            NonIndividual_sell_count=int(item[6]),
                                            Individual_sell_volume=int(item[7]),
                                            NonIndividual_sell_volume=int(item[8]), 
                                            proportion_buy_ind = int(item[3]) /(int(item[3]) + int(item[4]) ),
                                            proportion_sell_ind = int(item[7]) /(int(item[7]) + int(item[8]) )))
        except:pass

    clients = pd.DataFrame(clienttype)


    return clients 


def get_adjusted_single_ticker_history(stock_id):
    r = requests.get(f'http://members.tsetmc.com/tsev2/chart/data/Financial.aspx?i={stock_id}&t=ph&a=1')
    content= r.content.decode('utf-8')
    contentList= content.split(';')
    adjustedDict={}
    for element in contentList:
        eachday = element.split(',')
        adjustedDict[eachday[0]] = [int(float(element) )for element in eachday[1:]]
    df = pd.DataFrame(adjustedDict).T
    df.reset_index(inplace=True)
    df.columns= ['date','high','low','first','last','volume','close']
    df['date'] = pd.to_datetime(df['date'])
    df[df.columns[1:]] = df[df.columns[1:]].astype(float)
    df["return"] = df["close"].pct_change()
    df.set_index('date' , inplace=True)
    return df

