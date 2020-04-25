import sys
sys.path.insert(1, '/stock_analysis/GetStockData')

from datetime import datetime
import pandas as pd
from GetStockData import GetData

class Analysis(GetData):

    def __init__(self, symbol, start=datetime(2020,1,1), end=datetime.now()):
        self.data_gotten = False
        super().__init__(symbol, start, end)

    def get_hist_data(self):
        data = super().get_hist_data()
        self.data = data
        self.data_gotten = True

    def check_data_availability(self, data):
        if data is not None:
            return data
        if not self.data_gotten:
            self.get_hist_data()
        return self.data

    def Min_Max(self, data=None):
        """
        Return a list of Max/Min/Last Pricing information in a list
        """
        try:
            df = self.check_data_availability(data)

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
            return result
        
        except:
            pass

    # https://quant.stackexchange.com/questions/11264/calculating-bollinger-band-correctly
    def Bollinger_Band(self, window_size = 20, num_sd = 2, data=None):
        """
        returns a data frame with average, upper band, and lower band
        """
        try:
            df = self.check_data_availability(data)

            df['rolling_mean'] = df['Close'].rolling(window=window_size).mean()
            df['rolling_std']  = df['Close'].rolling(window=window_size).std()
            df['upper_band'] =  round(df['rolling_mean'] + ( df['rolling_std']*num_sd), 4)
            df['lower_band'] =  round(df['rolling_mean'] - ( df['rolling_std']*num_sd), 4)
            df = df.drop(columns=['rolling_std'])
            return df
        
        except:
            pass

    def BBand_Outliers(self, last_n_days = 3, window_size = 20, num_sd = 2, data=None):
        """
        Identify if the price was in or out from the bollinger band
        """
        try:
            df = self.Bollinger_Band(window_size, num_sd, data)
            subdf = df.tail(last_n_days).reset_index()
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
            pass


    def RSI(self, series=None, window=14, ewma=True):
        """
        Input: a pandas series of closing price data; window period defaulted as 14 days; default using ewma technique
        Function: Calculate RSI
        Output, a series of RSI data
        """
        # https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
        # Calculate difference and make the positive gains (up) and negative gains (down) Series
        if series is None:
            df = self.check_data_availability(None)
            series = df['Close']

        delta = series.diff().dropna(
        )  # alternative: delta = series.diff().fillna(0)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        if ewma:
            # Calculate the EWMA
            roll_up = up.ewm(com=window-1).mean()  # Close to Yahoo Finance
            roll_down = down.abs().ewm(com=window-1).mean()  # Close to Yahoo Finance
        else:
            roll_up = up.rolling(window_length).mean()
            roll_down = down.abs().rolling(window_length).mean()
        # Calculate the RSI based on EWMA
        RS = roll_up / roll_down
        RSI = round(100.0 - (100.0 / (1.0 + RS)), 2)
        return RSI

    def overbought_oversold(RSI_series, last_n_days = 5):
        """
        Input: A pandas series of RSI data; last n days
        Function: Identify if the stock is overbrought/ oversold or not
        Output: Indicator
        """
        sub = RSI_series[-last_n_days:]
        if any(sub <= 20):
            indicator = "Oversold"
        elif all(sub > 20) & any(sub <= 30):
            indicator = "Maybe Oversold"
        elif all(sub < 70) & any(sub >= 70):
            indicator = "Maybe Overbought"
        elif any(sub >= 80):
            indicator = "Overbought"
        else:
            indicator = None
        return indicator
