
class Candle: 
    def __init__(self, open:float, high:float, low:float, close:float, volume:int):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
class OrderStatus:
    def __init__(self, order_id:str, symbol:str, price:float, order_type:str, contracts:float):
        self.id = order_id
        self.symbol = symbol
        self.price = price
        self.order_type = order_type
        self.contracts = contracts