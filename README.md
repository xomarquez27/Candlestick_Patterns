# Candlestick Patterns

Find daily candlestick and volume patterns on stocks from daily close data (open, high, low, close, volume) as well as statistics on the 3, 5, and 10 day perfomance of the stock
after those pattern appears.

## Purpose
The reason for this project has been wanting to be alerted of specific candlestick pattern on stocks, so that a trade can be made based on the appearance of such pattern. However, the appearance of a pattern while interesting by itself does not provide enough info, or substance to make a trade based on just a visual pattern on a chart, therefore I wanted to see what was the historical performance of the stock after such pattern appeared to see if it would be worth it to make the trade, this project does all of that.


## Overview
This project currently uses the TD Ameritrade API to get the stocks daily end of day data onto a csv file, it also used an FTP (file transfer protocol) method before to update the csv files, this method is also included in the project. Both way update each individual stocks' csv file (how many depends on how many stocks you follow), then using pandas and numpy the program analyzes stocks csv data and find patterns that can be deduced from the price and volume data stored in each individual stock csv file. The program also finds out how many times those pattern have appeared in the past (depends on how much data is available) and it lists the average, best and worst performance of the stock, 3, 5, and 10 days after the pattern appears (based on the close price after the respective time period). The information can then be printed, stored into a file, or even sent out via tweet!

### Prerequisites
This project was developed on a Linux system, therefore it also works on Mac OS. There are a bunch of bash scripts which are the launching points of most of the program's functionalities, and work on schedule via crontab. The bash scripts can be translated to Windows by using the equivalent Powershell, and Task Scheduler. I do not provide these equivalents and you must make them yourself if using Windows. As an alternative, you could use the [Windows Susbsystem for Linux.](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

### APIs
This program uses both the TD Ameritrade and Twitter APIs, the Twitter API is not necessary unless you are tweeting out your findings, but the TD Ameritrade API is needed to get the daily close data unless you are using the FTP method via eoddata.com. To use the TD Ameritrade API, you must create or have an account with them. For the Twitter API, you will need the tweepy.json file referenced on several scripts on your project directory. This file should contain your consumer key, secret and access key and secret in the following format:

>{
	"consumer_key": "randomstring"
	"consumer_secret": "randomstring"
	"access_key": "randomstring"
	"access_secret": "randomstring"
>}

### Libraries
The program uses bash and Python 3.7 to do most of its functionalities, because of several Python libraries not being part of the standard library, there are a few imports that take place on basically all of the Python scripts, these are:

> pandas
> numpy
> requests
> tweepy

You can install these libraries on your system or use a virtual environment, the remaining libraries are part of the standard library and are not listed here. Note that virtual environments are used in this project, they are activated at the start of some of the bash scripts.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. Read below for notes on how to deploy the project on a live system.

### Main Functionality:

1. To get started, you can download any stock daily close data on csv format from the NASDAQ website, just go to nasdaq.com/market-activity/stocks/spy/historical (replace spy with whichever stock you want). You can get up to 10 years of data (if available) on the NASDAQ website, however, for DJIA, COMP, SPX and VIX you can get over 20 years of data at wsj.com/market-data/quotes/index/DJIA/historical-prices Name all your files after the ticker symbol of the stock then the file extension e.g. AAPL.csv, AMZN.csv, TSLA.csv etc. etc.

2. Once you got all the stocks you want to follow, put them on a folder inside your project and run the Format.ipynb, this notebook has a couple of cells which format the csv file to a more usable format by rearranging and formatting the columns. This is necessary since csv files from NASDAQ have a $ on the price, and csv files from wsj have a leading whitespace in the column name, both of these things create perky bugs that can evade a beginner programmer. The script file is on notebook format since you will need to run different cells depending on where you get your data from, this might be turned into a Python script that takes into account the different sources and possibilities at a later time.

3. Once formatted, you want to place all your stock csv files on a folder inside your project, I call mine stock_data. Each csv file should consist of the following columns: Date, Open, High, Low, Close, Volume. The data should be ascending by date from top to bottom, so oldest data on first line, latest on the last line.

4. Once the stock files are in their proper folder, run stock_list.sh, this bash script takes the ticker symbol of every csv file and adds it to a text file called stocks.txt this file is used by the fetch_data.py script to fetch the close data of all the stocks on that text file via TD Ameritrade API, run this about 30 after market close to take into account after-hours trade volume and delayed data, this data will then be stored on a file called eod.csv. 

**Take into account that certain tickers are not the same under the TD Ameritrade API.** By example, the Dow Jones Industrial Average appears under '$DJI' and not 'DJIA, the Nasdaq cannot currently be fetched, so you could use '$NDX.X' instead of 'COMP'. 'SPX' becomes '$SPX.X', and 'VIX' is '$VIX.X'. I have dealt with these discrepancies already in the code.

5. Run updater.py to update every stock csv file with the latest day data from eod.csv

6. If you feel inclined to post anything to Twitter you can use poster.py to do so, granted that you have already set up Twitter API access and are using Tweepy, if you just want to print to the console or terminal, you can just comment out lines 7, 34, and 204 as well as uncomment line 203.


### Other Functions:

ftp_updater.py file uses ftp to update every stock csv file, I used it with the service from eoddata.com. You need to create a file called watchlist.csv and include all the stocks you want to follow there in the following format, ticker, exchange, company name (optional): AAPL, NASDAQ, Apple Inc. The code is well commented and every step is explained.

Gappers.py file fetches data upon market open via crontab morning_gaps.sh and tweets out which stocks are gapping more than 2.5% up or down. This file uses oauth to get an access token for real-time data and is only included as a reference.

latest_prices.sh file creates a latest_prices.txt file inside a logs/ folder (which you should have to avoid cluttering the project). The text file basically shows the last line out of every stock csv file and it is used to double check data.

launcher.sh file activates the virtual environment, then launches the main function of the program divided into fetch_data.py, update.py and poster.py and then deactivates the virtual environment and exits.

tailer.sh file is essentially the same as latest_prices.sh

validate.sh file creates missing_days.txt in which one can see which stocks were not updated with today's data if run after updater.py 



### Notes
This project was lots of fun to create since it is a very interesting subject to me and I am very passionate about the world of trading.
The findings of this project are tweeted out every day this includes, the daily finding on over 200 stocks (at the time of this writing) as well as the morning gappers, you can follow the account [@dailycandlestix](twitter.com/dailycandlestix).

### Authors
* Xavier Otero Marquez