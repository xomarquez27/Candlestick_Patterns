#!/bin/bash


echo "" > ./stocks.txt

for f in ./stock_data/*.csv; do echo $(basename $f .csv) >> ./stocks.txt; done;
