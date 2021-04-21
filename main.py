import requests       
import json           
import pandas as pd    
import numpy as np     
import matplotlib.pyplot as plt
import datetime as dt  

from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.ticker as ticker


def get_bars(symbol, interval):
   root_url = 'https://api.binance.com/api/v1/klines'
   url = root_url + '?symbol=' + symbol + '&interval=' + interval
   data = json.loads(requests.get(url).text)

   df = pd.DataFrame(data)
   df.columns = ['open_time',
                 'o', 'h', 'l', 'c', 'v',
                 'close_time', 'qav', 'num_trades',
                 'taker_base_vol', 'taker_quote_vol', 'ignore']

   df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]
   return df

def get_price(pair):
    return np.array(pair)

def get_EMA(pair_price, value):
    EMA = value*[None]

    for i in range(value, len(pair_price)):
        tempEMA = np.average(pair_price[i-20:i])
        EMA.append(tempEMA)

    return EMA

def get_std_deviation(pair_price, pair_EMA):
    
    squared_deviation = len(pair_price)*[None]
    
    for k in range(len(pair_price)):
        try:
            squared_deviation[k] = (pair_price[k]/pair_EMA[k] - 1)**2
        except:
            pass
    
    squared_deviation_filtered = list(filter(None, squared_deviation))
    variance = np.mean(squared_deviation_filtered)

    std_deviation = variance**0.5

    return std_deviation

def get_risk(pair_price, pair_EMA):
    
    deviation = len(pair_price)*[0]
    
    for k in range(len(pair_price)):
        try:
            deviation[k] = (pair_price[k] - pair_EMA[k])/pair_EMA[k]
        except:
            pass
    
    min_deviation = min(deviation)
    max_deviation = max(deviation)

    risk = len(pair_price)*[None]
    for l in range(len(pair_price)):
        risk[l] = (deviation[l] - min_deviation)/(max_deviation - min_deviation)

    return risk

def plot_pricevsEMA(pair_price, pair_EMA, color_scale, pair, timeframe, value, std_deviation, pair_time):
    cmap = cm.get_cmap('jet', 32)

    for j in range(len(pair_price)):
        if j < value:
            plt.plot(pair_time[j], pair_price[j], 'o', color = 'white')    
        else:
            plt.plot(pair_time[j], pair_price[j], 'o', color = cmap(color_scale[j]))
    
    ax = plt.gca()
    ax.set_facecolor('grey')
    ax.set_yscale('log')
      
    plt.title(pair[:-4] + r'/USDT: price, EMA' + str(value) + r' $\pm$ $\sigma$' + ' || ' + r'$\sigma$ = ' + str(std_deviation)[:5], fontsize = 16)

    cbar = plt.colorbar(cm.ScalarMappable(norm=None, cmap=cmap), ax=ax)
    cbar.ax.set_ylabel('RISK', rotation=0, fontsize = 14)
    

    ymin, ymax = 0.9*np.min(pair_price), 1.1*np.max(pair_price)

    z = []
    z_string = []
    for i in [0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.4, 2, 4, 7, 10, 15, 20, 30, 40, 50, 60, 80, 150, 300, 500, 750, 1000, 1500, 2000, 2500, 5000, 7500, 10000, 12500, 15000, 20000, 25000, 30000, 40000, 50000, 60000, 70000]:

        if i > ymin and i < ymax:
            z.append(i)
            z_string.append(str(i))
            
    ax.set_yticks(z)
    ax.set_yticklabels(z_string)        
    
    plt.plot(pair_time, pair_EMA, 'black')
    

def plot_onestddev(pair_EMA, std_deviation, pair_time):
    onestddevup = len(pair_EMA)*[None]
    onestddevdown = len(pair_EMA)*[None]

    for p in range(len(pair_EMA)):
        try:
            onestddevup[p] = (1 + std_deviation) * pair_EMA[p]
            onestddevdown[p] = (1 - std_deviation) * pair_EMA[p]
        except:
            continue

    plt.plot(pair_time, onestddevup, 'red')
    plt.plot(pair_time, onestddevdown, 'green')

def showplot():
    plt.grid()
    plt.show()
    
    
############################################################################################################
pairlist = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'LINKUSDT', 'DOTUSDT']

for pair in pairlist:
    timeframe = '1d'
    EMA_value = 30

    pair_bars_full = get_bars(pair, timeframe)
    pair_bars = pair_bars_full['c'].astype('float')

    pair_time = pair_bars.index

    pair_price = get_price(pair_bars)
    pair_EMA = get_EMA(pair_price, EMA_value)
    std_deviation = get_std_deviation(pair_price, pair_EMA)

    pair_risk = get_risk(pair_price, pair_EMA)

    plot_pricevsEMA(pair_price, pair_EMA, pair_risk, pair, timeframe, EMA_value, std_deviation, pair_time)
    plot_onestddev(pair_EMA, std_deviation, pair_time)
    
    showplot()
