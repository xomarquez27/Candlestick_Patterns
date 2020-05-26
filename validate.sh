#!/bin/bash
# 
# Run after data update to validate if all files in stock_data were updated
# with the current day's data. If not, it creates a text file containing all
# the names of the files which data has not been updated.

touch ./logs/missing_days.txt
today=$(date +%d)

for f in ./stock_data/*.csv; do data=$(tail -1 "$f") && day=${data:8:2};
	if [ "$day" -ne "$today" ]; 
		then echo $(basename $f .csv) $(date +%F) >> ./logs/missing_days.txt
	fi
done;

unset today; unset data; unset day;
