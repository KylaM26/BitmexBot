
from os import name
import os.path
import numpy as np
import pandas as pd
from datetime import datetime
from pandas.tseries.frequencies import get_period_alias
from requests.api import get
from Connector.Bitmex import Bitmex

from Connector.Client import Client

class Database: 
    def __init__(self, path:str):
        self.path = path
        
    def add_data(self, client:Client, symbol:str, start=None, end=None):
        symbol_is_valid = False
        symbol = symbol.upper()
        
        for instrument in client.instruments:
            if instrument.upper() == symbol:
                symbol_is_valid = True
                break
            
        if symbol_is_valid == False:
            print("Symbol '{}' is not a valid symbol in the {} database.".format(symbol, client.name))
            return None
        # If start and end are none -> Get latest data
        # If start -> Write older data
        filename = client.name + "_" + symbol + ".csv"

        if self._does_file_exist(file=filename) == False: # Inital data
            data = client.get_historical_data(symbol=symbol, start=start, end=end)
            return self._write_initial_data(client, filename, symbol, data)
        elif self._does_file_exist(file=filename) == True and start is None and end is None:
            return self._write_latest_data(client=client, symbol=symbol)
        elif self._does_file_exist(file=filename) == True and start is not None and end is None:
            return self._write_older_data(client=client, symbol=symbol, start_date=start)
        elif self._does_file_exist(file=filename) == True and start is not None: # There was a new start and end so create a new data set or a specific start and end time was given
            data = client.get_historical_data(symbol=symbol, start=start, end=end)
            return self._write_initial_data(client, filename, symbol, data)
        else:
            print("You must supply a start time if you supply an end time.")
            
    def get_data(self, client_name:str, symbol:str):
        filename =  client_name + "_" + symbol + ".csv"
        return pd.read_csv(self.path + filename, parse_dates=True, index_col=["date"])
    
    def _write_latest_data(self, client: Client,  symbol:str):
        symbol = symbol.upper()
 
        dataframe = self.get_data(client_name=client.name, symbol=symbol)
        start_date = dataframe.head(1).index
        data = client.get_historical_data(symbol=symbol, start=start_date)
        df = pd.DataFrame(data=data)
       # df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y-%m-%dT%H:%M:%S.%fZ')
        df.set_index("date",inplace=True)
        df.to_csv(self.path + client.name + '_' + symbol + '.csv')
        return self.get_data(client_name=client.name, symbol=symbol)
            
    def _write_older_data(self, client: Client, symbol:str, start_date:str):
        symbol = symbol.upper()
        
        data= client.get_historical_data(symbol=symbol, start=start_date)
        df = pd.DataFrame(data=data)
        df.set_index("date",inplace=True)
        df.to_csv(self.path + client.name + '_' + symbol + '.csv')
        return self.get_data(client_name=client.name, symbol=symbol)
        
    def _write_initial_data(self, client:Client, filename:str, symbol:str, data):
        df = pd.DataFrame(data=data)
        df.set_index("date",inplace=True)
        df.to_csv(self.path + filename)
        return self.get_data(client_name=client.name, symbol=symbol)
   
    def _does_file_exist(self, file:str) -> bool:
        return os.path.exists(path=self.path + file)
    
    def _is_file_empty(self, file:str):
        if(self._does_file_exist(self.path + file)):
            if os.stat(self.path + file).st_size == 0:
                return True
            else:
                return False
        return False