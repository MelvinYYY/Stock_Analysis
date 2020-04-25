import shutil
import urllib.request as request
from contextlib import closing
import pandas as pd


def update_tickers_list():
    '''
    Get the most up-to-date tickers list from the ftp, which updates every business day
    '''
    # Download the nasdaq tickers list
    with closing(
            request.urlopen(
                'ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt')
    ) as r:
        with open('GetStockData/nasdaq_tickers.txt', 'wb') as f:
            shutil.copyfileobj(r, f)

    # Download the nyse and other tickers list
    with closing(
            request.urlopen(
                'ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt')
    ) as r:
        with open('GetStockData/other_tickers.txt', 'wb') as f:
            shutil.copyfileobj(r, f)


def get_nasdaq_tickers():
    '''
    Return: a pandas dataframe ticker list
    '''
    # read with pandas
    nasdaq_tickers = pd.read_csv('nasdaq_tickers.txt', sep='|', header=0)
    # remove the footage
    nasdaq_tickers = nasdaq_tickers[:-1]
    # Apply filters
    nasdaq_tickers = nasdaq_tickers[
        (nasdaq_tickers['Nasdaq Traded'] != 'N') & # This is the BRK.A. Don't have enough money to buy anyway...
        (nasdaq_tickers['Test Issue'] != 'Y') &
        (nasdaq_tickers['ETF'] != 'Y') &   # Not interested in ETF
        (~nasdaq_tickers['Security Name'].str.contains('ETN')) & # Not Interested in ETN as well
        (~nasdaq_tickers['Security Name'].str.contains('Preferred Share')) &
        (~nasdaq_tickers['Security Name'].str.contains('Preferred Series')) &
        (~nasdaq_tickers['Security Name'].str.contains('Warrants'))&
        (~nasdaq_tickers['Symbol'].str.contains('\.')) &
        (~nasdaq_tickers['Symbol'].str.contains('\$'))
    ]
    nasdaq_tickers = nasdaq_tickers.reset_index(drop=True)  # reset index
    return nasdaq_tickers.iloc[:, 1:3]


def get_other_tickers():
    # read with pandas
    nyse_tickers = pd.read_csv('other_tickers.txt', sep='|', header=0)
    # remove the footage
    nyse_tickers = nyse_tickers[:-1]
    # Apply filters
    nyse_tickers = nyse_tickers[
        (nyse_tickers['Test Issue'] != 'Y') & (nyse_tickers['ETF'] != 'Y')&  # Not interested in ETF
        (~nyse_tickers['Security Name'].str.contains('ETN')) &  # Not Interested in ETN as well
        (~nyse_tickers['Security Name'].str.contains('Preferred Share')) &
        (~nyse_tickers['Security Name'].str.contains('Preferred Series')) &
        (~nyse_tickers['Security Name'].str.contains('Warrants')) &
        (~nyse_tickers['ACT Symbol'].str.contains('\.')) &
        (~nyse_tickers['ACT Symbol'].str.contains('\$'))
    ]
    nyse_tickers = nyse_tickers.reset_index(drop=True)  # reset index
    # Rename
    df = nyse_tickers.iloc[:, 0:2]
    df.columns = ['Symbol', 'Security Name']
    return df
