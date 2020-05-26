#!/bin/bash
# 
# Run after data update to check the last row on every stock csv file.
# I use this for a quick verification of the prices

touch ./logs/latest_prices.txt
today=$(date +%D)

echo -e "Prices on $today \nTicker\tOpen\tHigh\tLow\tClose\tVolume \n" > ./logs/latest_prices.txt
for f in ./stock_data/*.csv; do info=$(tail -1 "$f") && echo -e "$(basename $f .csv):" ${info:11:-1} >> ./logs/latest_prices.txt;
done;