#!/bin/bash

touch ./logs/closing_prices.txt


echo -e "Ticker,Date,Open,High,Low,Close,Volume" > ./logs/closing_prices.txt
for f in ./stock_data/*.csv; do 
	echo "$(basename "$f" .csv), $(tail -1 "$f")" >> ./logs/closing_prices.txt;
done;