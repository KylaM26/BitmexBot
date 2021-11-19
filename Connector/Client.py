
import typing
import logging
from enum import Enum

from datetime import date, datetime

class OrderSide(Enum):
    BUY = 0
    SELL = 1
class OrderType(Enum):
    MARKET = 0
    LIMIT = 1
    
class Client: 
    def __init__(self, name:str, base_url:str, test_net_url:str, websocket:typing.Union[str, None], testnet_websocket:typing.Union[str, None], public_key:str, secret_key:str, use_testnet=True):
        if use_testnet:
            self.base_url = test_net_url
            self.websocket_url = testnet_websocket
        else:
            self.base_url = base_url
            self.websocket_url = websocket
        
        self._public_key = public_key
        self._secret_key = secret_key
        
        self.name = name
        
        self.instruments = self._get_instruments()
        self.orders = self.get_orders()
        
        self.websocket = None
        
        self.logger = self.create_logger()
        self.realtime_data = None
        
    def _get_instruments(self):
        pass
    
    def place_order(self, side:OrderSide, symbol:str, contracts:float, order_type:OrderType, price=None, tif="GoodTillCancel"):
        pass
    
    def cancel_order(self, order_id: typing.Union[str, None]=None):
        pass
    
    def get_orders(self, only_open_orders=True):
        pass
    
    def get_historical_data(self, symbol:str, start:typing.Union[str, None]=None, end:typing.Union[str, None]=None, candle_count=1000):
       pass

    def create_logger(self):
        # Prints logger info to terminal
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Change this to DEBUG if you want a lot more info
        ch = logging.StreamHandler()
        
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # add formatter to ch
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger