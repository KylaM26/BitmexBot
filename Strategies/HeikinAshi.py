
import typing

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

class HeikinAshi:
    def __init__(self, dataframe:pd.DataFrame):
        self.dataframe = dataframe
        
        self.dataframe["buy_and_hold_returns"] = self.dataframe["close"].pct_change()
        self.dataframe["buy_and_hold_creturns"] = self.dataframe["buy_and_hold_returns"].cumsum().apply(np.exp)
        
        self.dataframe["heikin_open"] = (self.dataframe["open"].shift(-1) + self.dataframe["close"].shift(-1)) / 2
        self.dataframe["heikin_close"] = (self.dataframe["open"] + self.dataframe["close"] + self.dataframe["high"] + self.dataframe["low"]) / 4
        
    def backtest(self):
        # Post the signals
        # when the data changed, post buy and sell
        
        self.dataframe["signals"] = np.where(self.dataframe["heikin_close"] < self.dataframe["heikin_open"], 1, -1)
        self.dataframe["signals"] = self.dataframe["signals"].shift(1)
        
        buy_prices = []
        sell_prices = []
        
        for index in range(0, self.dataframe.shape[0]):
            price = self.dataframe["close"][index]
            if index != 0:
                if self.dataframe["signals"][index - 1] != self.dataframe["signals"][index]:
                    if self.dataframe["signals"][index] == 1:
                        buy_prices.append(price)
                        sell_prices.append(np.nan)
                    elif self.dataframe["signals"][index] == -1:
                        buy_prices.append(np.nan)
                        sell_prices.append(price)
                else:
                    buy_prices.append(np.nan)
                    sell_prices.append(np.nan)
            else:
                buy_prices.append(np.nan)
                sell_prices.append(np.nan)
                        
        self.dataframe["buy_signal_price"] = buy_prices
        self.dataframe["sell_signal_price"] = sell_prices
        
    def plot_buy_and_sell(self,figsize=(15, 10), style="seaborn-pastel"):
        plt.style.use(style=style)
        plt.figure(figsize=figsize)
        
        plt.plot(self.dataframe.index, self.dataframe["close"])
        
        plt.scatter(self.dataframe.index, self.dataframe["buy_signal_price"], marker="^", color="green", alpha=1)
        plt.scatter(self.dataframe.index, self.dataframe["sell_signal_price"], marker="v", color="red", alpha=1)
        
        plt.xlabel = "Date"
        plt.ylabel = "Close Prices $USD"
        
        plt.xticks(rotation=45)
        plt.show()