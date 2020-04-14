import pandas_datareader.data as web
from datetime import datetime
import pandas as pd

class GetData:

    def __init__(self, symbol, start=datetime(2020,1,1), end=datetime.now()):
        self.symbol = symbol
        self.dtf = start
        self.dtt = end

    def get_hist_data(self):
        try:
            df = web.DataReader(self.symbol, 'yahoo', self.dtf, self.dtt) # This is easier to use
            df = df.reset_index(drop = False)
            return df
        except:
            raise Exception('Could not get ' + str(self.symbol) + ' from Yahoo Finance')
