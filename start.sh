#!/bin/bash
cd /cmcnews/NewsLogger.CMC/
git pull
pip install -r requirements.txt
sleep 1
clear
python3 main.py