#1 LIBRARIES

import pandas as pd
import datetime
import os
import logging
from ftplib import FTP
from config import ftp_user, ftp_pass

#2 Logging
logging.basicConfig(filename="app.log", filemode="a", format="%(asctime)s)"
                   " - %(name)s - %(levelname)s - %(message)s")


#3 Watchlist

# Take every csv file in stock_data, get the ticker from the filename
# append the ticker to a list, then sort alphabetically
tickers = [] 
for file in os.listdir('./stock_data'):
	if file.endswith('.csv'):
		tickers.append(file.split('.csv')[0])
tickers.sort()

watchlist = pd.read_csv('watchlist.csv', names=['Ticker', 'Exchange', 'Company Name'])

try:
	for t in tickers:
		if t not in watchlist['Ticker'].values:
			raise ValueError
except ValueError:
	print(f'{t}.csv present in stock_data folder, but not in watchlist.csv, update watchlist.csv before continuing.')

#4 Exchanges

# Place tickers from watchlist into their respective exchanges
# for more efficiency during step #7
AMEX = []
INDEX = []
NASDAQ = []
NYSE = []

for row in watchlist.itertuples():
	eval(row.Exchange).append(row.Ticker)

#5 Removes prior day exchange files if any prior to downloading new data
for item in os.listdir('.'):
	if item.endswith('.txt'):
		os.remove(item)


#6 Get EOD data from exchanges listed on step #4

# Concatenate today's date with '_' and '.txt' to produce the suffix
# that will be appended to the filename 
today = datetime.date.today()
suffix = '_' + today.strftime('%Y') + today.strftime('%m') + today.strftime('%d') + '.txt'
exchanges = ['AMEX', 'INDEX', 'NASDAQ', 'NYSE']

# WARNING: Be sure to delete exchange .txt files from day prior before running this code (step 5 above).

ftp = FTP('ftp.eoddata.com')
ftp.login(ftp_user, ftp_pass)

try:
    for exch in exchanges: # AMEX, INDEX, NASDAQ, NYSE
        filename = exch + suffix # AMEX_20191213.txt, INDEX_20191213.txt, ...
        download = open(filename, 'wb')
        ftp.retrbinary('RETR ' + filename, download.write, 1024)
        download.close()

    ftp.quit()
except ftplib.error_perm:
    logging.error(f"Could not retrieve the following file {filename}", exc_info=True)    

#7 Update watchlist with latest data

file_location = 'stock_data/'
cols = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']

daydata = pd.DataFrame(columns=cols)

for file in os.listdir('.'):
    if file.endswith('.txt'):
        market = pd.read_csv(file, names=cols, parse_dates=[1]) # NASDAQ_20200205.txt
        for t in eval(file.split('_')[0]): # Every stock in AMEX[], NASDAQ[], etc, etc.
            target = pd.read_csv(file_location + t + '.csv', parse_dates=[0])
            daydata = market.loc[market['Symbol'] == t, "Date":"Volume"]
            target = target.append(daydata, ignore_index=True, sort=False)
            target['Date'] = target['Date'].dt.date
            target.to_csv(path_or_buf=file_location + t + '.csv', index=False, date_format='%Y-%m-%d')