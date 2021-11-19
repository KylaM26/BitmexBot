import numpy as pd
import pandas as pd

from Connector.Client import OrderSide, OrderType
from Connector.Bitmex import Bitmex
from Database.Database import Database

PUBLIC_KEY = "evIWFAJHrRxf5Hx2Jkc7M809"
SECRET_KEY = "vfVfBTyKgxMDYFurPy7EV1gl8VQJ7IuMQAL4UCvPB5kuG1fG"
bitmex_client = Bitmex(public_key=PUBLIC_KEY, secret_key=SECRET_KEY)
rt_data = bitmex_client.get_realtime_data(symbol="XBTUSD")
