from Connector.Client import Client, OrderSide, OrderType

import numpy as np 
import pandas as pd
from Utility.Utility import str2int64time, datetime2str, int64time2str
import json
import typing
import requests
import time
import hashlib
import urllib.parse
import hmac
from datetime import date, datetime
from urllib.parse import _DefragResultBase, non_hierarchical, urlencode

class Kucoin(Client):
    def __init__(self, public_key:str, secret_key:str, phrase:str, use_testnet=True):
        super().__init__("Kucoin", "https://api.kucoin.com", "https://openapi-sandbox.kucoin.com", None, None, public_key, secret_key, use_testnet)
        self.phrase = phrase
        
    def _request(self, method:str, endpoint:str, params=None, use_headers=False):
        headers = dict()
        
        if use_headers:
            expires = str(int(round(time.time()) + 5))
            signature = self._generate_signature(method=method, endpoint=endpoint, data=params or '')
            headers = {
                "api-expires": expires,
                "api-key": self._public_key,
                "api-signature": signature
            }
        
        response = requests.request(method=method, url=self.base_url+endpoint, params=params, headers=headers)
            
        if response.status_code == 200:
            return response.json()
        else:
            print(response.text)
        
        return None
        
    def _get_instruments(self):
        super()._get_instruments()
        
        params = { "market" : "USDS"}
        
        instruments_response = self._request(method="GET", endpoint="/api/v1/symbols", params=params)
        instruments = []
        
        if instruments_response is not None:
            for instrument in instruments_response["data"]:
                instruments.append(instrument["symbol"])
                
        return instruments
    
    def get_historical_data(self, symbol:str, start:typing.Union[str, None]=None, end:typing.Union[str, None]=None, granularity="1min", candle_count=1500):
        super().get_historical_data(symbol, start, end, candle_count)
        
        collect_rate = 2
        
        if start is not None:
            start = str2int64time(start)
        if end is not None:
            end = str2int64time(end)
            
        params = {
            "type": granularity,
            "symbol": symbol.upper()
        }
        
        last_start_time = None
        candles = []
        counter = 0
        end_point = "/api/v1/market/candles"
        
        if start is None and end is None:
            last_start_time = str2int64time(datetime2str(datetime.today()))
            now = str2int64time(datetime2str(datetime.now()))
            params["endAt"] = now
            
            while(True):   
                params["startAt"] = last_start_time   
               
                data_response = self._request("GET", end_point, params=params)

                if data_response is None:
                    print("No candle data is availiable.")
                    break
                else:
                    counter += 1
        
                for candle in data_response["data"]:            
                    data = dict()
                    data["date"] =   int64time2str(int(candle[0]))
                    data["open"] =   candle[1]
                    data["high"] =   candle[2]
                    data["low"] =    candle[3]
                    data["close"] =  candle[4]
                    data["volume"] = candle[5]
                    candles.append(data)
                
                if len(candles) > 0:
                    last_start_time = candles[0]["date"]
                    print("Iteration {}: {} candles collected | Total candles {}".format(counter, len(data_response["data"]), len(candles)))
                
                if (len(data_response) < candle_count):
                    if len(candles) > 0:
                        candles.pop(0)
                    break
                
                time.sleep(collect_rate)    
        elif start is not None and end is None:
            last_start_time = start
            now = str2int64time(datetime2str(datetime.now()))
            params["endAt"] = now
            
            while(True):   
                params["startAt"] = last_start_time   
                data_response = self._request("GET", end_point, params=params)
                
                if data_response is None:
                    print("No candle data is availiable.")
                    break
                else:
                    counter += 1
                    
                for candle in data_response["data"]:            
                    data = dict()
                    data["date"] =   int64time2str(int(candle[0]))
                    data["open"] =   candle[1]
                    data["high"] =   candle[2]
                    data["low"] =    candle[3]
                    data["close"] =  candle[4]
                    data["volume"] = candle[5]
                    candles.append(data)
                
                if len(candles) > 0:
                    last_start_time = candles[0]["date"]
                    
                print("Iteration {}: {} candles collected | Total candles {}".format(counter, len(data_response["data"]), len(candles)))
                         
                if(len(data_response) < candle_count):
                    if len(candles) > 0:
                        candles.pop(0)
                    break 
                
                time.sleep(collect_rate)
        else:
            last_start_time = start
            params["endAt"] = end
            
            while(True):  
                params["startAt"] = last_start_time   
               
                data_response = self._request("GET", end_point, params=params)

                if data_response is None:
                    print("No candle data is availiable.")
                    break
                else:
                    counter += 1
                
                for candle in data_response["data"]:            
                    data = dict()
                    data["date"] =   int64time2str(int(candle[0]))
                    data["open"] =   candle[1]
                    data["high"] =   candle[2]
                    data["low"] =    candle[3]
                    data["close"] =  candle[4]
                    data["volume"] = candle[5]
                    candles.append(data)
                
                if len(candles) > 0:
                    last_start_time = candles[0]["date"]
                    print("Iteration {}: {} candles collected | Total candles {}".format(counter, len(data_response["data"]), len(candles)))
                
                if (len(data_response) < candle_count):
                    break
                
                time.sleep(collect_rate) 

        return candles
                
        
        
        
    
        