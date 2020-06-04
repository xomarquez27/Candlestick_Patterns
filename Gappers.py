#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import datetime, time, json, requests, tweepy
from config import client_id
from os import listdir


with open('token.txt', 'r') as json_file:
    token_data = json.load(json_file)

# Load refresh token
refresh_token = token_data['refresh_token']


# define the endpoint
url = r'https://api.tdameritrade.com/v1/oauth2/token'

#define the headers
headers ={'Content-Type':"application/x-www-form-urlencoded"}

#define the payload
payload = {'grant_type':'refresh_token',
           'refresh_token':refresh_token,
           'client_id': client_id,
           'redirect_uri':'http://127.0.0.1'}

#post the data to get the token

authReply = requests.post(url, headers = headers, data = payload)

# convert token data (json string) to dictionary

decoded_content = authReply.json()

# Access Token
access_token = decoded_content['access_token']

# Access Token expiration is 30 mins (1800 seconds)
access_token_expiration = decoded_content['expires_in']

# Use the access token expiration to calculate the time it expires (local)
access_token_renewal_date = datetime.datetime.fromtimestamp(time.time() + access_token_expiration)

headers['Authorization'] = 'Bearer '+str(decoded_content['access_token'])


def get_quotes(**kwargs):
    url = 'https://api.tdameritrade.com/v1/marketdata/quotes'

    arguments = {'apikey': client_id}

    symbol_list = [symbol for symbol in kwargs.get('symbol')]
    arguments.update({'symbol': symbol_list})

    return requests.get(url, headers=headers, params=arguments).json()


# Read stocks to update from file
with open('stocks.txt', newline='') as f:
    lines = f.read().splitlines()
    stocks = list(lines[1:])


# Break into chunks as to not call the function with too many symbols
def chunks(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


# Create Close Date Dict
close_data = {}

for chunk in chunks(stocks, 15):
    data = get_quotes(symbol=chunk)
    close_data.update(data)


df = pd.DataFrame.from_dict(close_data, orient='index', columns=['symbol', 'openPrice', 'closePrice', '52WkHigh'])
df['Pct Change'] = (df['openPrice'] / df['closePrice']) - 1

file_location = 'stock_data/'

stock_20_day_high = {}
stock_50_day_high = {}
stock_100_day_high = {}

for file in listdir('./stock_data/'):
    if file.endswith('.csv'):
        data = pd.read_csv(file_location + file, parse_dates=[0])
        data = data.iloc[::-1]
        data = data.iloc[:100]
        stock_20_day_high[file.split(".csv")[0]] = data[:20]['High'].max()
        stock_50_day_high[file.split(".csv")[0]] = data[:50]['High'].max()
        stock_100_day_high[file.split(".csv")[0]] = data['High'].max()

df['20 Day High'] = df['symbol'].map(stock_20_day_high)
df['50 Day High'] = df['symbol'].map(stock_50_day_high)
df['100 Day High'] = df['symbol'].map(stock_100_day_high)


def twitter_auth():
	"""Twitter session authorization"""

	config_file = '.tweepy.json'
	with open(config_file) as fh:
			config = json.load(fh)

	auth = tweepy.OAuthHandler(
			config['consumer_key'], config['consumer_secret']
	)
	auth.set_access_token(
			config['access_token'], config['access_token_secret']
	)

	return tweepy.API(auth)


twitter = twitter_auth()


content = []
content.append("Morning gaps:\n")
char_count = len(content[0])
for t in df[['symbol', 'Pct Change']].values:
    if abs(t[1]) > .025:
            line = f"${t[0]} {t[1]:,.2%}\n"
            content.append(line)
            char_count += len(line)
            if char_count >= 265:
                twitter.update_status("".join(content))
                content.clear()
                char_count = 0
                content.append("Morning gaps:\n")
twitter.update_status("".join(content))


# Breakout alerts
content.clear()
char_count = 0

for t in df[['symbol', 'openPrice', '20 Day High', '50 Day High', '100 Day High', '52WkHigh']].values:
    if t[1] > t[2]:
        if t[1] > t[5]:
            line = f'${t[0]} New 52 Wk high!\n'
        elif t[1] > t[4]:
                line = f'${t[0]} Alert: Open > 100 day high\n'
        elif t[1] > t[3]:
            line = f'${t[0]} Alert: Open > 50 day high\n'
        else:
            line = f'${t[0]} Alert: Open > 20 day high\n'
        # Count characters
        char_count += len(line)
        content.append(line)
        if char_count > 242:
            twitter.update_status("".join(content))
            content.clear()
            char_count = 0
twitter.update_status("".join(content))