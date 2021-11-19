from Connector.Client import Client, OrderSide, OrderType

import json
import typing
import requests
import time
import hashlib
import urllib.parse
import hmac
from urllib.parse import non_hierarchical, urlencode

from bitmex_websocket import BitMEXWebsocket

class Bitmex(Client): 
    def __init__(self, public_key:str, secret_key:str, use_testnet=True):
        super().__init__("Bitmex", "https://www.bitmex.com", "https://testnet.bitmex.com", "wss://ws.bitmex.com/realtime", "wss://ws.testnet.bitmex.com/realtime", public_key, secret_key, use_testnet)
        
        if self._request("GET", "/api/v1", None):
            print("Successfully connected to the {} API.".format(self.name))
        
    def _generate_signature(self, method:str, endpoint:str, data:typing.Dict) -> str:
        expires = int(round(time.time()) + 5)
        parsedURL = urllib.parse.urlparse(endpoint)
        path = parsedURL.path
        
        if parsedURL.query:
            path = path + '?' + parsedURL.query

        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf8')

        message = method + endpoint + "?" + urlencode(data) + str(expires) if len(data) > 0 else method + endpoint + str(expires)
        signature = hmac.new(self._secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return signature
        
    def _request(self, method:str, endpoint:str, params=None):
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
        instruments_response = self._request("GET", "/api/v1/instrument", None)
        instruments = []
        
        for instrument in instruments_response:
            instruments.append(instrument["symbol"])
            
        return instruments
    
    def place_order(self, side:OrderSide, symbol:str, contracts:float, order_type:OrderType, price=None, tif="GoodTillCancel"):
        super().place_order(side, symbol, contracts, order_type, price, tif)
        
        params = {
            "symbol": symbol.upper(),
            "side": "Buy" if side == OrderSide.BUY else "Sell",
            "orderQty": contracts,
            "ordType": "Market" if order_type == OrderType.MARKET else "Limit"
        }
        
        if order_type == OrderType.LIMIT: # If a price is given, assume limit order in code and bitmex also assumes limit if price is given.
            params["price"] = float(price)
            params["timeInForce"] = tif
             

        endpoint = '/api/v1/order'
        order = self._request("POST", endpoint, params)
        
        if order is not None:
            order_dict = dict()
            order_dict["id"] = order["orderID"]
            order_dict["timestamp"] = order["timestamp"]
            order_dict["account"] = order["account"]
            order_dict["symbol"] = order["symbol"]
            order_dict["side"] = order["side"]
            order_dict["contracts"] = order["orderQty"]
            order_dict["type"] = order["ordType"]
            order_dict["status"] = order["ordStatus"]
            self.orders[order["orderID"]] = order_dict
        else:
            print("Failed to place order.")
        
        return order

    def cancel_order(self, order_id: typing.Union[str, None]=None):
        super().cancel_order(order_id)
        if order_id is not None:
            endpoint = "/api/v1/order"
        else:
            endpoint = "/api/v1/order/all"
        
        params = dict()
        params = { "orderID" : order_id }
            
        response = self._request("DELETE", endpoint, params)
        self.orders.pop(order_id)

        return response
        
    def get_orders(self, only_open_orders=True):
        super().get_orders(only_open_orders)
        endpoint = '/api/v1/order'
        
        params = None
        
        if only_open_orders:
            params = dict()
            filters = { "open" : True }
            params["filter"] = json.dumps(filters)
        
        orders = self._request("GET", endpoint, params)
        
        if orders is not None:
            data = dict()

            for order in orders:
                order_dict = dict()
                order_dict["id"] = order["orderID"]
                order_dict["timestamp"] = order["timestamp"]
                order_dict["account"] = order["account"]
                order_dict["symbol"] = order["symbol"]
                order_dict["side"] = order["side"]
                order_dict["contracts"] = order["orderQty"]
                order_dict["type"] = order["ordType"]
                order_dict["status"] = order["ordStatus"]
                data[order["orderID"]] = order_dict

        return data
            
    def get_historical_data(self, symbol:str, start:typing.Union[str, None]=None, end:typing.Union[str, None]=None, candle_count=1000):
        super().get_historical_data(symbol, start, end, candle_count)
        params = {
            "binSize": "1m",
            "symbol": symbol.upper(),
            "count": candle_count,
        }
        
        last_start_time = None
        candles = []
        counter = 0
        end_point = "/api/v1/trade/bucketed"
        
        if start is None and end is None:
            last_start_time = datetime.today().date()
            end = datetime.now()
            params["endTime"] = end
            
            while(True):   
                params["startTime"] = last_start_time   
               
                data_response = self._request("GET", end_point, params=params)
                if data_response is None:
                    print("No candle data is availiable.")
                    break
        
                for candle in data_response:            
                    data = dict()
                    data["date"] =   candle["timestamp"]
                    data["open"] =   candle["open"]
                    data["high"] =   candle["high"]
                    data["low"] =    candle["low"]
                    data["close"] =  candle["close"]
                    data["volume"] = candle["volume"]
                    candles.append(data)
                
                if len(candles) > 0:
                    last_start_time = candles[-1]["date"]
                    print("Iteration {}: {} candles collected | Total candles {}".format(counter, len(data_response), len(candles)))
                
                if (len(data_response) < candle_count):
                    candles.pop()
                    break
                
                counter += 1        
        elif start is not None and end is None:
            last_start_time = start
            end = datetime.now()
            params["endTime"] = end
            
            while(True):   
                params["startTime"] = last_start_time   
                data_response = self._request("GET", end_point, params=params)
                
                if data_response is None:
                    print("No candle data is availiable.")
                    break

        
                for candle in data_response:            
                    data = dict()
                    data["date"] =   candle["timestamp"]
                    data["open"] =   candle["open"]
                    data["high"] =   candle["high"]
                    data["low"] =    candle["low"]
                    data["close"] =  candle["close"]
                    data["volume"] = candle["volume"]
                    candles.append(data)
                
                last_start_time = candles[-1]["date"]
                print("Iteration {}: {} candles collected | Total candles {}".format(counter, len(data_response), len(candles)))
                counter += 1  
                
                        
                if(len(data_response) < candle_count):
                    candles.pop()
                    break 
        else:
            last_start_time = start
            params["endTime"] = end
            
            while(True):   
                params["startTime"] = last_start_time   
               
                data_response = self._request("GET", end_point, params=params)

                if data_response is None:
                    print("No candle data is availiable.")
                    break
        
                for candle in data_response:            
                    data = dict()
                    data["date"] =   candle["timestamp"]
                    data["open"] =   candle["open"]
                    data["high"] =   candle["high"]
                    data["low"] =    candle["low"]
                    data["close"] =  candle["close"]
                    data["volume"] = candle["volume"]
                    candles.append(data)
                
                if len(candles) > 0:
                    last_start_time = candles[-1]["date"]
                    print("Iteration {}: {} candles collected | Total candles {}".format(counter, len(data_response), len(candles)))
                
                if (len(data_response) < candle_count):
                    break
                
                counter += 1

        return candles
            
    def get_realtime_data(self, symbol:str):
        ws = BitMEXWebsocket(endpoint=self.websocket_url, symbol=symbol, api_key=self._public_key, api_secret=self._secret_key)
        
        self.realtime_data = dict()
        self.realtime_data["instrument"] = ws.get_instrument()
        self.realtime_data["ticker"] = ws.get_ticker()
        self.realtime_data["funds"] = ws.funds()
        self.realtime_data["market_depth"] = ws.market_depth()
        self.realtime_data["open_orders"] = ws.open_orders(clOrdIDPrefix=None)
        self.realtime_data["recent_trades"] = ws.recent_trades()
        
        while(ws.ws.sock.connected):
            self.realtime_data["ticker"] = ws.get_ticker()
            self.logger.info("Ticker: %s" % self.realtime_data["ticker"])
            
            if ws.api_key:
                self.realtime_data["funds"] = ws.funds()
                self.logger.info("Funds: %s" % self.realtime_data["funds"])
                
            self.realtime_data["market_depth"] = ws.market_depth()
            self.logger.info("Market Depth: %s" % self.realtime_data["market_depth"])
                
            self.realtime_data["open_orders"] = ws.open_orders(clOrdIDPrefix=None)
            self.logger.info("Open Trades: %s" % self.realtime_data["open_orders"])  
            
            self.realtime_data["recent_trades"] = ws.recent_trades()
            self.logger.info("Recent Trades: %s\n\n" % self.realtime_data["recent_trades"])
                
            time.sleep(1000)