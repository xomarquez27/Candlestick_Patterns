#!/bin/bash
# 
# This bash script runs to check which files' oldest data is less than five years old
# By example: After running it will create a text file in logs called since_year.txt
# this file will contain the names of all stocks which do not have data older than 2015
# this serves to check which files can be updated with 10 year data.
# However, take note that recent ipos such as BYND, LYFT, UBER will appear there.

touch ./logs/since_year.txt

five_years_ago=2015

for f in ./stock_data/*.csv; do data=$(head -2 "$f" | tail -1) && year=${data:0:4};
	if [ "$year" -gt "$five_years_ago" ]; 
		then echo $(basename $f .csv) >> ./logs/since_year.txt
	fi
done;

unset today; unset data; unset day;
