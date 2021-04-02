import os
import pandas as pd

cols = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
location = './stock_data/'
source = pd.read_csv('./eod.csv', names=cols, parse_dates=[1])

# Allows for the issue with TD Ameritrade API using different symbols on the following tickers
# to not affect files names as they are stored under the key name
source.replace({'Symbol':{'$DJI': 'DJI', '$SPX.X': 'SPX', '$VIX.X': 'VIX', 'COMP:GIDS'}}, inplace=True)

for file in os.listdir('./stock_data/'):
	if file.endswith('.csv'):
		target = pd.read_csv(location + file, parse_dates=[0], sep=',')
		daydata = source.loc[source['Symbol'] == file.split('.csv')[0], "Date":"Volume"]
		target = target.append(daydata, ignore_index=True, sort=False)
		target['Date'] = pd.to_datetime(target['Date'])
		target['Date'] = target['Date'].dt.date
		target.to_csv(path_or_buf=location + file, index=False, date_format='%Y-%m-%d')
