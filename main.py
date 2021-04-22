import requests       
import json           
import pandas as pd    
import numpy as np     
import matplotlib.pyplot as plt
import datetime as dt 
from matplotlib import cm


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

def get_SMA(pair_price, value):
    SMA = value*[None]

    for i in range(value, len(pair_price)):
        tempSMA = np.average(pair_price[i-20:i])
        SMA.append(tempSMA)

    return SMA

def get_std_deviation(pair_price, pair_SMA):
    
    squared_deviation = len(pair_price)*[None]
    
    for k in range(len(pair_price)):
        try:
            squared_deviation[k] = (pair_price[k]/pair_SMA[k] - 1)**2
        except:
            pass
    
    squared_deviation_filtered = list(filter(None, squared_deviation))
    variance = np.mean(squared_deviation_filtered)

    std_deviation = variance**0.5

    return std_deviation

def get_risk(pair_price, pair_SMA, SMA_value):
    
    deviation = len(pair_price)*[0]
    min_deviation = len(pair_price)*[0]
    max_deviation = len(pair_price)*[0]
    
    for k in range(len(pair_price)):
        try:
            deviation[k] = pair_price[k]/pair_SMA[k] - 1
        except:
            pass

        if k > 4*SMA_value:
            amplifier = 0.2*pair_SMA[k]/min(pair_SMA[k - 3*SMA_value:k])

        elif k > SMA_value:
            amplifier = 0.2*pair_SMA[k]/min(pair_SMA[SMA_value:k])
        
        else:
            amplifier = 0.2*pair_price[k]/min(pair_price[:k+1])
        
        deviation[k] = amplifier + deviation[k]

        min_deviation[k] = min(deviation[:k+1]) - 0.01
        max_deviation[k] = max(deviation[:k+1]) + 0.01

    risk = len(pair_price)*[None]
    for l in range(len(pair_price)):
        risk[l] = (deviation[l] - min_deviation[l])/(max_deviation[l] - min_deviation[l])

    return risk

def get_ratio(pair_price, pair_SMA):

    pair_ratio = len(pair_price)*[0]
    for i in range(len(pair_price)):
        try:
            pair_ratio[i] = (pair_price[i]/pair_SMA[i])
        except:
            continue

    return pair_ratio

def get_normal_ratio(pair_price, pair_SMA):
    pair_ratio = get_ratio(pair_price, pair_SMA)

    min_ratio = min(pair_ratio)
    max_ratio = max(pair_ratio)

    normal_ratio = len(pair_ratio)*[None]

    for o in range(len(pair_ratio)):
        normal_ratio[o] = (pair_ratio[o] - min_ratio)/(max_ratio - min_ratio)


    return normal_ratio

def plot_pricevsSMA(pair_price, pair_SMA, color_scale, pair, timeframe, value, std_deviation, pair_time):
    cmap = cm.get_cmap('jet', 32)

    for j in range(len(pair_price)):
        if j < value:
            plt.plot(pair_time[j], pair_price[j], 'o', color = 'white')    
        else:
            plt.plot(pair_time[j], pair_price[j], 'o', color = cmap(color_scale[j]))
    
    ax = plt.gca()
    ax.set_facecolor('grey')
    ax.set_yscale('log')
      
    
    plt.title(pair[:-4] + r'/USDT: price, SMA' + str(value) + r' $\pm$ $\sigma$' + ' || ' + r'$\sigma$ = ' + str(std_deviation)[:5], fontsize = 16)

    cbar = plt.colorbar(cm.ScalarMappable(norm=None, cmap=cmap), ax=ax)
    cbar.ax.set_ylabel('RISK', rotation=0, fontsize = 14)
    
    ymin, ymax = 0.9*np.min(pair_price), 1.1*np.max(pair_price)

    z = []
    z_string = []
    for i in [0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.4, 2, 4, 7, 10, 15, 20, 30, 40, 50, 60, 80, 150, 300, 500, 750, 1000, 1500, 2000, 2500, 2800, 5000, 7500, 10000, 12500, 15000, 20000, 25000, 30000, 40000, 50000, 60000, 70000]:

        if i > ymin and i < ymax:
            z.append(i)
            z_string.append(str(i))
            
    ax.set_yticks(z)
    ax.set_yticklabels(z_string)        
    
    plt.plot(pair_time, pair_SMA, 'black')
    

def plot_onestddev(pair_SMA, std_deviation, pair_time):
    onestddevup = len(pair_SMA)*[None]
    onestddevdown = len(pair_SMA)*[None]

    for p in range(len(pair_SMA)):
        try:
            onestddevup[p] = (1 + std_deviation) * pair_SMA[p]
            onestddevdown[p] = (1 - std_deviation) * pair_SMA[p]
        except:
            continue

    plt.plot(pair_time, onestddevup, 'red')
    plt.plot(pair_time, onestddevdown, 'green')

def showplot():
    plt.grid()
    plt.show()
    
    
############################################################################################################
pairlist = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'LINKUSDT', 'DOTUSDT']
#pairlist = ['XMRUSDT', 'AVAXUSDT', 'FILUSDT', 'BNBUSDT', 'LUNAUSDT']
#pairlist = ['XLMUSDT', 'NEOUSDT', 'VETUSDT', 'TRXUSDT', 'SOLUSDT']
#pairlist = ['ONEUSDT', 'ALGOUSDT', 'XRPUSDT', 'DOGEUSDT']

for pair in pairlist:
    timeframe = '1d'
    SMA_value = 30

    pair_bars_full = get_bars(pair, timeframe)
    pair_bars = pair_bars_full['c'].astype('float')

    pair_time = pair_bars.index

    pair_price = get_price(pair_bars)
    pair_SMA = get_SMA(pair_price, SMA_value)
    std_deviation = get_std_deviation(pair_price, pair_SMA)

    pair_risk = get_risk(pair_price, pair_SMA, SMA_value)

    plot_pricevsSMA(pair_price, pair_SMA, pair_risk, pair, timeframe, SMA_value, std_deviation, pair_time)
    plot_onestddev(pair_SMA, std_deviation, pair_time)
    
    showplot()
