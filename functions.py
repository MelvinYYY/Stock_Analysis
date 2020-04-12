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
        self.start = start
        self.end = end
        self.all_min_max = []
        
    def get_hist_data(self):
        """
        Use pandas' DataReader to collect histocial data for a stock
        Input: Stock Symbol, start time in datetime format, end time in datetime format
        Output: A pandas dataframe contains histocial stock data, including date, open price,
                the highest price, the lowest price, close price, adjusted close price, volume. 
        """
        df = web.DataReader(self.symbol, 'yahoo', self.start, self.end) # This is easier to use
        df = df.reset_index(drop = False)
        return df
    
    def get_Min_and_Max(self):
        """ 
        Return a list of Max/Min/Last Pricing information in a list
        """ 
        try:
            df = self.get_hist_data()
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
            df = self.get_hist_data()
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
                indicator = None

            return [self.symbol, indicator]
        
        except:
            print(" ")
            
            
#### Useful functions to run in multiprocessing 

def All_Min_and_Max(symbol, start = datetime(2020,1,1), end = datetime.now()):
    amam = Stock(symbol, start, end )
    return amam.get_Min_and_Max()


def All_BBands_Outliers(symbol, start = datetime(2020,3,1), end = datetime.now(), last_n_days = 3):
    return Stock(symbol, start, end).BBand_Outliers(last_n_days = last_n_days)


def RSI(series, window=14, ewma=True):
    """
    Input: a pandas series of closing price data; window period defaulted as 14 days; default using ewma technique
    Function: Calculate RSI 
    Output, a series of RSI data 
    """
    # https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
    # Calculate difference and make the positive gains (up) and negative gains (down) Series
    delta = series.diff().dropna(
    )  # alternative: delta = series.diff().fillna(0)
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    if ewma == True:  # as default
        # Calculate the EWMA
        roll_up1 = up.ewm(com=window-1).mean()  # Close to Yahoo Finance
        roll_down1 = down.abs().ewm(com=window-1).mean()  # Close to Yahoo Finance

        # Calculate the RSI based on EWMA
        RS1 = roll_up1 / roll_down1
        RSI1 = round(100.0 - (100.0 / (1.0 + RS1)), 2)

        return RSI1

    else:  # Use SMA
        # Calculate the SMA
        roll_up2 = up.rolling(window_length).mean()
        roll_down2 = down.abs().rolling(window_length).mean()

        # Calculate the RSI based on SMA
        RS2 = roll_up2 / roll_down2
        RSI2 = round(100.0 - (100.0 / (1.0 + RS2)), 2)

        return RSI2

def overbought_oversold(series, last_n_days = 5):
    """
    Input: A pandas series of RSI data; last n days
    Function: Identify if the stock is overbrought/ oversold or not
    Output: Indicator
    """
    sub = series[-last_n_days:]
    
    try:
        if any(sub <= 20) == True:
            indicator = "Oversold"

        elif all(sub > 20) == True & any(sub <= 30) == True:
            indicator = "Maybe Oversold"

        elif all(sub < 70) == True & any(sub >= 70) == True:
            indicator = "Maybe Overbought"

        if any(sub >= 80) == True:
            indicator = "Overbought"
        
        return indicator
    
    except:
        return None
        

def all_RSI_indicators(symbol, start = datetime(2020,1,1), end = datetime.now(), last_n_days = 5):
    """
    Input: symbol, start date, end date, last n days
    Function: Work with multiprocessing to calculate RSI indicator for all stock symbol
    Output: symbol and indicator
    """
    df =  functions.Stock(symbol,start = start, end = end).get_hist_data()
    rsi = RSI(df['Close'])
    ind = overbought_oversold(rsi, last_n_days = last_n_days)
    return [symbol, ind]
