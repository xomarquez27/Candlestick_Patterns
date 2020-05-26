#!/bin/bash
cd ~/Desktop/Python/

source API_env/bin/activate

cd Stock_Scanner/

python3 fetch_data.py && sleep 5 && python3 updater.py && sleep 5 && python3 poster.py

deactivate

bash validate.sh
