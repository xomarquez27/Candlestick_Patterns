#!/bin/bash
cd ~/Desktop/Python/

source API_env/bin/activate

cd Stock_Scanner/

python3 Gappers.py

deactivate