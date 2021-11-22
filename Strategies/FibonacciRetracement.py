from os import altsep
import typing

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

class FibonacciRetracement:
    def __init__(self, dataframe: pd.DataFrame, src="close"):
        self.dataframe = dataframe
        
        self.max_price    = self.dataframe[src].max()
        self.min_price    = self.dataframe[src].min()
        min_max_diff      = self.max_price - self.min_price
        
        # Calculating the retracement levels
        self.first_level  = self.max_price - min_max_diff * 0.236
        self.second_level = self.max_price - min_max_diff * 0.382
        self.third_level  = self.max_price - min_max_diff * 0.5
        self.fourth_level = self.max_price - min_max_diff * 0.618
        
        # Using the MACD for this fibonacci strategy
        self.fast_ema    = self.dataframe[src].ewm(span=12, adjust=False).mean()
        self.slow_ema    = self.dataframe[src].ewm(span=26, adjust=False).mean()
        self.macd        = self.fast_ema - self.slow_ema
        self.signal_line = self.macd.ewm(span=9, adjust=False).mean()
        
        self.dataframe["buy_and_hold_returns"]  = self.dataframe["close"].pct_change()
        self.dataframe["buy_and_hold_creturns"] = self.dataframe["buy_and_hold_returns"].cumsum().apply(np.exp)
        self.dataframe["macd"]                  = self.macd
        self.dataframe["signal_line"]           = self.signal_line
        
    def get_fib_lvls_for_price(self, price:float):
        if price >= self.first_level:
            return (self.max_price, self.first_level)
        elif price >= self.second_level:
            return (self.first_level, self.second_level)
        elif price >= self.third_level:
            return (self.second_level, self.third_level)
        elif price >= self.fourth_level:
            return (self.third_level, self.fourth_level)
        else:
            return (self.fourth_level, self.min_price)
    
    def backtest(self):
        # If signal line crosses above the MACD and the current price crossed above or below the last fib level
        # If signal line crosses below the MACD and the current price crossed above or below the last fib level
        
        buy_list = []
        sell_list = []
        flag = 0
        last_buy_price = 0
        upper_level, lower_level = None, None
        
        for index in range(0, self.dataframe.shape[0]):
            # Get the price of the close index
            price = self.dataframe["close"][index] 
            
            # If this the first index, get the current levels for that price.
               
            # Else if the other prices are greater than or equal to the upper level 
            #or less than or equal to lower level, this means the price hit a
            #a new fibonacci level.
        
            if index == 0:
                upper_level, lower_level = self.get_fib_lvls_for_price(price=price)
                buy_list.append(np.nan)
                sell_list.append(np.nan)
            elif price >= upper_level or price <= lower_level: 
                # If the conditons are met and we purchased
                if self.dataframe["signal_line"][index] > self.dataframe["macd"][index] and flag == 0:
                    last_buy_price = price
                    buy_list.append(price)
                    sell_list.append(np.nan)
                    flag = 1
                elif self.dataframe["signal_line"][index] < self.dataframe["macd"][index] and flag == 1 and price >= last_buy_price:
                    buy_list.append(np.nan)
                    sell_list.append(price)
                    flag = 0
                else:
                    buy_list.append(np.nan)
                    sell_list.append(np.nan)
            else:
                buy_list.append(np.nan)
                sell_list.append(np.nan)   
                
            upper_level, lower_level = self.get_fib_lvls_for_price(price=price)
            
        self.dataframe["buy_signal_price"] = buy_list
        self.dataframe["sell_signal_price"] = sell_list
                    
    def plot(self, figsize=(15,10), style="seaborn-pastel"):
        plt.style.use(style)
        plt.figure(figsize=figsize)
        
        # Setting a subplot for the fib retracement levels
        plt.subplot(2, 1, 1)
        
        # Plotting the close price
        plt.plot(self.dataframe.index, self.dataframe["close"])
        
        # Plotting the fib retracement lines
        plt.axhline(self.max_price, linestyle="--", color='red', alpha=0.5)
        plt.axhline(self.first_level, linestyle="--", color='orange', alpha=0.5)
        plt.axhline(self.second_level, linestyle="--", color='yellow', alpha=0.5)
        plt.axhline(self.third_level, linestyle="--", color='green', alpha=0.5)
        plt.axhline(self.fourth_level, linestyle="--", color='blue', alpha=0.5)
        plt.axhline(self.min_price, linestyle="--", color='purple', alpha=0.5)
        
        plt.ylabel("Fibonacci")
        plt.xticks(rotation=45)
        
        # Setting a subplot for the macd 
        plt.subplot(2, 1, 2)
        
        plt.plot(self.dataframe.index, self.macd)
        plt.plot(self.dataframe.index, self.signal_line)
        
        plt.ylabel('MACD')
        plt.xticks(rotation=45)
        
        plt.show()
    
    def plot_buy_and_sell(self, figsize=(15,8), style="seaborn-pastel"):
        plt.style.use(style)
        plt.figure(figsize=figsize)
        
        plt.subplot(2, 1, 1)
        
        # Plotting the close price
        plt.plot(self.dataframe.index, self.dataframe["close"])
        
        # Plotting buy and sell signals
        plt.scatter(self.dataframe.index, self.dataframe["buy_signal_price"], color="green", marker="^", alpha=1)
        plt.scatter(self.dataframe.index, self.dataframe["sell_signal_price"], color="red", marker="v", alpha=1)
        
        # Plotting the fib retracement lines
        plt.axhline(self.max_price, linestyle="--", color='red', alpha=0.5)
        plt.axhline(self.first_level, linestyle="--", color='orange', alpha=0.5)
        plt.axhline(self.second_level, linestyle="--", color='yellow', alpha=0.5)
        plt.axhline(self.third_level, linestyle="--", color='green', alpha=0.5)
        plt.axhline(self.fourth_level, linestyle="--", color='blue', alpha=0.5)
        plt.axhline(self.min_price, linestyle="--", color='purple', alpha=0.5)
        
        plt.ylabel("Close Price $USD")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        
        plt.subplot(2, 1, 2)
        
        plt.plot(self.dataframe.index, self.macd)
        plt.plot(self.dataframe.index, self.signal_line)
        
        plt.ylabel('MACD')
        plt.xticks(rotation=45)
        
        plt.show()