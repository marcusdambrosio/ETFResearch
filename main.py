import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')
import pandas_datareader.data as web
import os
import sys
import datetime as dt
from dateutil.relativedelta import relativedelta
import itertools

ETFlist = ['QQQ', 'SPXL', 'SPXS', 'FDN', 'VGT',
           'RYT','FIVG', 'XLC','EMQQ','XBUY']

def pull_data(tickers, update = False):
    if 'DATA' not in os.listdir():
        os.mkdir('DATA')

    startDate = '01-01-2015'
    for ticker in tickers:
        if f'{ticker}.csv' in os.listdir('DATA') and update == False:
            print('Already have ', ticker)
            continue
        currData = web.DataReader(ticker, 'yahoo', startDate, dt.datetime.today())
        if 'Adj Close' in currData.columns:
            currData.rename(columns = {'Adj Close':'AdjClose'}, inplace = True)
        currData.to_csv(os.path.join('DATA', f'{ticker}.csv'))
        print('Successfully collected ', ticker)

    print('Data collecton complete.')


def overall_return(data, ticker = False, yearsBack = 5):
    if ticker:
        data = pd.read_csv(os.path.join('DATA', f'{ticker}.csv'), index_col = 'Date', parse_dates = True)
        # data['ts'] = data.index.values.astype(np.int64) / 10 ** 9
        # data['Date'] = data.index
        # data.set_index('ts', drop = True, inplace = True)
        return (data.AdjClose.values[-1] - data.loc[data.index[-1] - dt.timedelta(days = yearsBack*365), 'AdjClose']) /( data.loc[
            data.index[-1] - dt.timedelta(days = yearsBack*365), 'AdjClose']), data
    else:
        return (data.AdjClose.values[-1] - data.loc[data.index[-1] - dt.timedelta(days=yearsBack * 365), 'AdjClose']) / (data.loc[
            data.index[-1] - dt.timedelta(days=yearsBack * 365), 'AdjClose'])


def annualized_return(data, ticker = False, yearsBack = 5):
    '''This function calculates annualized returns.
    The default output will be [Average annual return, annual return stdev, list of annual returns].
    If a ticker is provided, the function will then load this ticker's price data and output this as well.'''
    if ticker:
        data = pd.read_csv(os.path.join('DATA', f'{ticker}.csv'), index_col='Date', parse_dates=True)
        # data['ts'] = df.index.values.astype(np.int64) / 10 ** 9
        # data.set_index('ts', drop = True, inplace = True)
        # print(data.index)
    '''HAVE TO FIGURE OUT INDEXING FOR THIS SHIT'''
    data.set_index('ts', drop = True, inplace = True)
    closes = data.AdjClose
    currYear = int(dt.datetime.today().year)
    startYear = currYear-int(yearsBack)
    startDates = [dt.datetime.strptime(f'01-01-{year}', '%m-%d-%Y') for year in np.arange(startYear, currYear+1)]
    endDates = [dt.datetime.strptime(f'12-31-{year}', '%m-%d-%Y') for year in np.arange(startYear, currYear)]
    endDates.append(dt.datetime.today())
    returns = []
    # sys.exit()
    for i in range(len(endDates)):
        returns.append((closes[endDates[i]] - closes[startDates[i]]) / closes[startDates[i]])

    returns.append((closes[-1] - closes[startDates[-1]])/closes[startDates[-1]]/
                   (relativedelta(closes[-1], closes[startDates[-1]]).years))

    if ticker:
        return np.mean(returns), np.stdev(returns), returns, data
    else:
        return np.mean(returns), np.stdev(returns), returns


def best_option(tickers, yearsBack, update = False):
    multindex = pd.MultiIndex.from_product([tickers,yearsBack], names = ['Ticker' , 'Years'])
    results = pd.DataFrame(index = ['Overall', 'Annualized', 'Variance'], columns = multindex)
    pull_data(tickers, update)
    for ticker in list(tickers):
        for year in list(yearsBack):
            print(year)
            currOverall, currData = overall_return(0, ticker = ticker, yearsBack=year)
            results.loc['Overall',  (ticker,year)] = currOverall
            try:
                avgAnnual, stdevAnnual, annuals = annualized_return(currData, yearsBack=year)
                results.loc['Annualized', (ticker, year)], results.loc['Variance', (ticker, year)] = avgAnnual, stdevAnnual**2

            except:
                print('annualized did not work')

    for metric in ['Overall', 'Annualized', 'Variance']:
        print(f"The best {metric} result is {results[results[metric] == results[metric].max()].index} with {results[metric]}.")


best_option(ETFlist, yearsBack=[1,3,5])