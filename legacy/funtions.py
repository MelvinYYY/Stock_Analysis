# https://plotly.com/~jackp/17421/plotly-candlestick-chart-in-python/#/

import pandas_datareader.data as web
from datetime import datetime
import numpy as np
import pandas as pd
import gc
import Utils

class Stock:

    def __init__(self, symbol, start, end):
        self.symbol = symbol
        self.dtf = start
        self.dtt = end
        self.all_min_max = []

    def get_quote(self):
        df = web.DataReader(self.symbol, 'yahoo', self.dtf, self.dtt) # This is easier to use
        df = df.reset_index(drop = False)
        return df

    def get_Min_and_Max(self):
        """
        Return a list of Max/Min/Last Pricing information in a list
        """
        try:
            df = self.get_quote()
            #df = df.reset_index()
            closeMax = df.iloc[df['Close'].idxmax()]
            closeMin = df.iloc[df['Close'].idxmin()]
            closeCurrent = df.iloc[-1,:]
            result = [self.symbol,
                     closeMax['Date'].date(), # Date of highest closing price
                     closeMax['Close'],       # Max closing price
                     closeMin['Date'].date(), # Date of lowest closing price
                     closeMin['Close'],       # Min closing Price
                     closeCurrent['Date'].date(), # Last Close price
                     closeCurrent['Close'],    # Last Close Price
                     round((closeMin['Close'] - closeMax['Close'])/closeMax['Close'], 4), # Precent change from high to low
                     round((closeCurrent['Close'] - closeMax['Close'])/closeMax['Close'], 4) # Precent change from high to current
                    ]

            # Remove varible
            del df
            del closeMax
            del closeMin
            del closeCurrent
            gc.collect()

            return result

        except:
            print('Could not get ' + str(self.symbol) + ' from Yahoo Finance')


    # https://quant.stackexchange.com/questions/11264/calculating-bollinger-band-correctly
    def add_Bollinger_Band(self, window_size = 20, num_sd = 2):
        """
        returns a data frame with average, upper band, and lower band
        """
        try:
            df = self.get_quote()
            df['rolling_mean'] = df['Close'].rolling(window=window_size).mean()
            df['rolling_std']  = df['Close'].rolling(window=window_size).std()
            df['upper_band'] =  round(df['rolling_mean'] + ( df['rolling_std']*num_sd), 4)
            df['lower_band'] =  round(df['rolling_mean'] - ( df['rolling_std']*num_sd),4)
            df = df.drop(columns=['rolling_std'])
            return df

        except:
            print('Could not get ' + str(self.symbol) + ' from Yahoo Finance')

    def BBand_Outliers(self, last_n_days = 3):
        """
        Identify if the price was in or out from the bollinger band
        """
        try:
            df = self.add_Bollinger_Band()
            subdf = df.iloc[-3:, ].reset_index()

            if subdf.loc[:, ['High', 'Low', 'Open', 'Close', 'upper_band']].drop(
                    'upper_band', 1).gt(subdf['upper_band'], 0).all(1).any() == True:
                indicator = "Above Upper Band"

            elif subdf.loc[:, ['High', 'Low', 'Open', 'Close', 'upper_band']].drop(
                    'upper_band', 1).gt(subdf['upper_band'], 0).any(1).any() == True:
                indicator = "On Upper Band"

            elif subdf.loc[:, ['High', 'Low', 'Open', 'Close', 'lower_band']].drop(
                    'lower_band', 1).lt(subdf['lower_band'], 0).all(1).any() == True:
                indicator = "Below Lower Band"

            elif subdf.loc[:, ['High', 'Low', 'Open', 'Close', 'lower_band']].drop(
                    'lower_band', 1).lt(subdf['lower_band'], 0).any(1).any() == True:
                indicator = "On Lower Band"

            else:
                indicator = " "

            return [self.symbol, indicator]

        except:
            print(" ")


#### Use functions

def All_Min_and_Max(symbol, start = datetime(2020,1,1), end = datetime.now()):
    amam = Stock(symbol, start, end )
    return amam.get_Min_and_Max()


def All_BBands_Outliers(symbol, start = datetime(2020,3,1), end = datetime.now(), last_n_days = 3):
    return Stock(symbol, start, end).BBand_Outliers(last_n_days = last_n_days)
