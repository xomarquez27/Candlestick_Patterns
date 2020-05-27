import pandas as pd
import numpy as np
import datetime
import os
import logging
import json
import tweepy

logging.basicConfig(filename="app.log", filemode="a", format="%(asctime)s)"
										" - %(name)s - %(levelname)s - %(message)s")



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


if __name__ == '__main__':
	# Post to twitter
	twitter = twitter_auth()
	file_location = 'stock_data/'
	for file in os.listdir('./stock_data/'):
		if file.endswith('.csv'):

			data = pd.read_csv(file_location + file, parse_dates=[0])
			data = data.iloc[::-1]
			data.reset_index(inplace=True, drop=True)
			data['Date'] = data['Date'].dt.date
			
			# Indicates if stock closed higher than day's open, not previous close.
			data['Day Close'] = np.where(data['Close'] > data['Open'], 'Up', 'Down')
			

			# Find hammer candlestick if open - low > (close - open) * 2 
			# if the hammer's shadow is at least 2 times greater than the size of the real body
			data['Hammer'] = np.where(data['Day Close'] == 'Up', data['Open'] - data['Low'] >= ((data['High'] - data['Open']) * 2), False)

			data['Inverted Hammer'] = np.where(data['Day Close'] == 'Up', data['High'] - data['Close'] >= ((data['Close'] 
																				 - data['Low']) * 2), False)

			data['Marubozu'] = np.where((data['Open'] == data['Low']) & (data['High'] == data['Close']), True, False)

			data['Dragonfly Doji'] = np.where((data['High'] <= data['Open'] * 1.0015)
																				&	(data['Close'] >= data['Open'] * 0.9985), True, False)

			data['Engulfing'] = np.where((data['Day Close'].shift(-1) == 'Down') & 
																	(data['Close'] > data['Open'].shift(-1)) & 
																	(data['Open'] < data['Close'].shift(-1)), True, False)

			data['Piercing Line'] = np.where((data['Day Close'].shift(-1) == 'Down') &
															 (data['Close'] > data['Close'].shift(-1) + 
															 ((data['Open'].shift(-1) -
															 data['Close'].shift(-1)) * 0.50)) & 
															 (data['Close'] < data['Open'].shift(-1))
															 & (data['Open'] < data['Close'].shift(-1)), True, False)

			data['Harami'] = np.where((data['Day Close'] == 'Up') &
																(data['Day Close'].shift(-1) == 'Down') & 
																(data['Low'] > data['Close'].shift(-1)) &
																(data['High'] < data['Open'].shift(-1)), True, False)

			data['Three White Soldiers'] = np.where((data['Day Close'] == 'Up') & (data['Open'] > data['Open'].shift(-1)) & 
                                                (data['Open'] < data['Close'].shift(-1)) & (data['Day Close'].shift(-1) == 'Up') &
                                                (data['Open'].shift(-1) > data['Open'].shift(-2)) & 
                                                (data['Open'].shift(-1) < data['Close'].shift(-2)), True, False)

			data['Morning Star'] = np.where((data['Day Close'] == 'Up') & (data['Day Close'].shift(-2) == 'Down') & 
															(data['Day Close'].shift(-1) == 'Up') & 
															(data['Close'].shift(-1) < data['Close'].shift(-2)) &
															(data['Open'] > data['Close'].shift(-2)) &
															(data['Close'] > data['Close'].shift(-2)), True, False)
            
      # Open is higher than any of the previous 20 highs and it closes above the previous close
			data['Minor Breakout'] = data['Open'].gt(data['High'][::-1].shift().rolling(20).max()) & (data['Close'] > data['Close'].shift(-1))
            
      # Open is higher than any of the previous 50 highs and it closes above the previous close
			data['Major Breakout'] = data['Open'].gt(data['High'][::-1].shift().rolling(50).max()) & (data['Close'] > data['Close'].shift(-1))

			data['Bull Flagpole'] = np.where((data['Day Close'] == 'Up') &
                                ((data['Close'] - data['Open']) >= (((((data['High'].shift(-1) - data['Low'].shift(-1)) +
                                (data['High'].shift(-2) - data['Low'].shift(-2)) +
                                (data['High'].shift(-3) - data['Low'].shift(-3)))) / 3) * 2.5)) &
                                (data['Open'] >= data['Low'].shift(-1)), True, False)

      # Close is lower than any of the previous 20 lows
			data['Minor Breakdown'] = data['Close'].lt(data['Low'][::-1].shift().rolling(20).min())
            
      # Close is lower than any of the previous 50 lows
			data['Major Breakdown'] = data['Close'].lt(data['Low'][::-1].shift().rolling(50).min())

			data['Bear Flagpole'] = np.where((data['Day Close'] == 'Down') & 
                                ((data['Open'] - data['Close']) >= ((((data['High'].shift(-1) - data['Low'].shift(-1)) +
                                (data['High'].shift(-2) - data['Low'].shift(-2)) +
                                (data['High'].shift(-3) - data['Low'].shift(-3))) / 3) * 2.5)) &
                                (data['Open'] <= data['High'].shift(-1)), True, False)

			# Price and volume increase for the past 3 days 
			data['Rising Price and Volume'] = np.where((data['Close'] > data['Close'].shift(-1)) &
			                                           (data['Close'].shift(-1) > data['Close'].shift(-2)) &
			                                           (data['Close'].shift(-1) > data['Close'].shift(-2)) &
			                                           (data['Volume'] > data['Volume'].shift(-1)) &
			                                           (data['Volume'].shift(-1) > data['Volume'].shift(-2)), True, False)

			# Price increase, volume decrease for the past 3 days
			data['Rising Price, Declining Volume'] = np.where((data['Close'] > data['Close'].shift(-1)) &
			                                                  (data['Close'].shift(-1) > data['Close'].shift(-2)) &
			                                                  (data['Close'].shift(-2) > data['Close'].shift(-3)) &
			                                                  (data['Volume'] < data['Volume'].shift(-1)) &
			                                                  (data['Volume'].shift(-1) < data['Volume'].shift(-2)), True, False)

			# Volume decrease, price decrease for the past 3 days
			data['Lower Prices Lower Volume'] = np.where((data['Close'] < data['Close'].shift(-1)) &
			                                             (data['Close'].shift(-1) < data['Close'].shift(-2)) &
			                                             (data['Close'].shift(-2) < data['Close'].shift(-3)) &
			                                             (data['Volume'] < data['Volume'].shift(-1)) &
			                                             (data['Volume'].shift(-1) < data['Volume'].shift(-2)), True, False)

			# Price decrease, volume increase for the past 3 days
			data['Lower Prices Higher Volume'] = np.where((data['Close'] < data['Close'].shift(-1)) &
			                                              (data['Close'].shift(-1) < data['Close'].shift(-2)) &
			                                              (data['Close'].shift(-2) < data['Close'].shift(-3)) &
			                                              (data['Volume'] > data['Volume'].shift(-1)) &
			                                              (data['Volume'].shift(-1) > data['Volume'].shift(-2)), True, False)

			# Volume is greater than 2.5 times average daily volume
			data['Above Avg Volume'] = np.where(data['Volume'] > ((data['Volume'].mean() * 2.5)), True, False)

			# Volume is lower than half the average daily volume
			data['Below Avg Volume'] = np.where(data['Volume'] < ((data['Volume'].mean() * 0.5)), True, False)


			data['Hanging Man'] = np.where((data['Day Close'] == 'Down') & 
														 ((data['Close'] - data['Low']) >= ((data['Open'] - data['Close']) * 2)) & 
														 ((data['High'] - data['Open']) < (data['Open'] - data['Close']) * 0.50),True, False)

			data['Bearish Engulfing'] = np.where((data['Day Close'].shift(-1) == 'Up') &
													 (data['Close'] < data['Open'].shift(-1)) &
													 (data['Open'] > data['Close'].shift(-1)), True, False)

			data['Gravestone Doji'] = np.where((data['Low'] >= data['Open'] * 0.9985) &
																(data['Close'] <= data['Open'] * 1.0015), True, False)

			data['Bearish Harami'] = np.where((data['Day Close'] == 'Down') & (data['Day Close'].shift(-1) == 'Up') 
																				& (data['High'] < data['Close'].shift(-1)) 
																				& (data['Low'] > data['Open'].shift(-1)), True, False)

			data['Dark Cloud Cover'] = np.where((data['Day Close'] == 'Down') & (data['Day Close'].shift(-1) == 'Up') &
                                    (data['Open'] > data['Close'].shift(-1)) & (data['Close'] >= (((data['Close'].shift(-1) -
                                    data['Open'].shift(-1)) * .5) + data['Open'].shift(-1))) & (data['Close'] < data['Close'].shift(-1)), True, False)

			data['Three Black Crows'] = np.where((data['Day Close'] == 'Down') & (data['Open'] > data['Close'].shift(-1)) &
												(data['Open'] < data['Open'].shift(-1)) & (data['Day Close'].shift(-1) == 'Down') &												(data['Close'] < data['Close'].shift(-1)) & (data['Day Close'].shift(-1) == 'Down') &
												(data['Open'].shift(-1) > data['Close'].shift(-2)) & (data['Open'].shift(-1) < data['Open'].shift(-2)) &
												(data['Day Close'].shift(-2) == 'Down') & (data['Close'].shift(-1) < data['Close'].shift(-2)), True, False)

			data['Evening Star'] = np.where((data['Day Close'] == 'Down') 
																			& (data['Day Close'].shift(-2) == 'Up') 
																			& (data['Day Close'].shift(-1) == 'Down') 
																			& (data['Close'].shift(-1) > data['Close'].shift(-2)) 
																			& (data['Open'] < data['Close'].shift(-1)) 
																			& (data['Close'] > data['Open'].shift(-2)), True, False)
			
			day_pattern = [data.columns[(data == True).iloc[0]]][0]
			content = []
			if day_pattern.empty:
				pass
			else:
				for i in day_pattern:
					content.append(f'${file.split(".csv")[0]} {i} Pattern \n')
					content.append(f'Daily appearances since {data.iloc[-1,0]}: {data[i].sum()}\n')

					# Dataframe with all days in which the pattern is True
					performance = pd.DataFrame(data.loc[data[i] == True])

					# Grab the close from 5 days after a pattern occurs and make result be the difference in price
					# from the close of the day of the pattern and that close 5 days after the pattern
					performance['Five Days'] = data.shift(5)[data[i] == True]['Close']
					performance['Result'] =  performance['Five Days'] - performance['Close']
					content.append(f"Performance (Close) 5 days later \u00B1:\n")
					content.append(f"Avg: {performance['Result'].mean():.2f}\n")
					content.append(f"Worst: {performance['Result'].min():.2f}\n")
					content.append(f"Best: {performance['Result'].max():.2f} \n\n")

					# Same concept as above but using 10 days after
					performance['Ten Days'] = data.shift(10)[data[i] == True]['Close']
					performance['Result'] = performance['Ten Days'] - performance['Close']
					content.append(f"10 days later:\n")
					content.append(f"Avg: {performance['Result'].mean():.2f}\n")
					content.append(f"Worst: {performance['Result'].min():.2f}\n")
					content.append(f"Best: {performance['Result'].max():.2f} \n\n")

					performance['30 Days'] = data.shift(30)[data[i] == True]['Close']
					performance['Result'] =  performance['30 Days'] - performance['Close']
					content.append(f"30 days later:\n")
					content.append(f"Avg: {performance['Result'].mean():.2f}\n")
					content.append(f"Worst: {performance['Result'].min():.2f}\n")
					content.append(f"Best: {performance['Result'].max():.2f}\n")

					# print("".join(content))
					twitter.update_status("".join(content))
					content.clear()