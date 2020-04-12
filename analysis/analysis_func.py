from datetime import datetime
import pandas as pd
from get_data import Quote

class Analysis(Quote):

    def __init__(self, symbol, start=datetime(2020,1,1), end=datetime.now()):
        self.quote_gotten = False
        super().__init__(symbol, start, end)

    def get_quote(self):
        quote_df = super().get_quote()
        self.quote = quote_df
        self.quote_gotten = True

    def Min_Max(self, quote_df=None):
        """
        Return a list of Max/Min/Last Pricing information in a list
        """
        if self.quote_gotten:
            df = self.quote
        elif quote_df is not None:
            df = quote_df
        else:
            self.get_quote()
            df = self.quote

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

    # https://quant.stackexchange.com/questions/11264/calculating-bollinger-band-correctly
    def Bollinger_Band(self, window_size = 20, num_sd = 2, quote_df=None):
        """
        returns a data frame with average, upper band, and lower band
        """
        if self.quote_gotten:
            df = self.quote
        elif quote_df is not None:
            df = quote_df
        else:
            self.get_quote()
            df = self.quote

        df['rolling_mean'] = df['Close'].rolling(window=window_size).mean()
        df['rolling_std']  = df['Close'].rolling(window=window_size).std()
        df['upper_band'] =  round(df['rolling_mean'] + ( df['rolling_std']*num_sd), 4)
        df['lower_band'] =  round(df['rolling_mean'] - ( df['rolling_std']*num_sd), 4)
        df = df.drop(columns=['rolling_std'])
        return df

    def BBand_Outliers(self, last_n_days = 3, window_size = 20, num_sd = 2, quote_df=None):
        """
        Identify if the price was in or out from the bollinger band
        """
        df = self.Bollinger_Band(window_size, num_sd, quote_df)
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
            indicator = " "

        return [self.symbol, indicator]
