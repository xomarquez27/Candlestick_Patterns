import requests, csv, datetime
from config.py import client_id

# This is your api key
key = client_id


def get_quotes(**kwargs):
    url = 'https://api.tdameritrade.com/v1/marketdata/quotes'

    arguments = {'apikey': key}

    symbol_list = [symbol for symbol in kwargs.get('symbol')]
    arguments.update({'symbol': symbol_list})

    return requests.get(url, params=arguments).json()


# The following tickers (keys) can only be found on the TD Ameritrade API under the respective (values).
replacements = {'DJI': '$DJI', 'COMP': '$NDX.X', 'SPX': '$SPX.X', 'VIX': '$VIX.X'}

# Read stocks to update from file
with open('stocks.txt', newline='') as f:
    lines = f.read().splitlines()
    stocks = list(lines[1:])
    for ticker in stocks:
        if ticker in replacements:
            stocks[stocks.index(ticker)] = replacements[ticker]


# Break into chunks as to not call the function with too many symbols
def chunks(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


# Create Close Date Dict
close_data = {}

for chunk in chunks(stocks, 10):
    data = get_quotes(symbol=chunk)
    close_data.update(data)

today = datetime.date.today().strftime('%Y-%m-%d')

with open('eod.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    for ticker in close_data:
        if ticker in ['$DJI', '$NDX.X', '$SPX.X', '$VIX.X']:
            writer.writerow([close_data[ticker]['symbol'], today, close_data[ticker]['openPrice'],
                                        close_data[ticker]['highPrice'], close_data[ticker]['lowPrice'],
                                        close_data[ticker]['lastPrice'], '0'])
        else:
            writer.writerow([close_data[ticker]['symbol'], today, close_data[ticker]['openPrice'],
                             close_data[ticker]['highPrice'], close_data[ticker]['lowPrice'],
                             close_data[ticker]['regularMarketLastPrice'], close_data[ticker]['totalVolume']])
