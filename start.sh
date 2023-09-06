#!/bin/bash
cd /cmcnews/NewsLogger.CMC/
git pull
pip install -r requirements.txt
sleep 1
clear
python3 main.py


# #! /bin/bash
# echo Stated
# while true
# do
#     if [ $(date +%H) -eq 01 ]
#     then
#         echo Running Script Now
#         ./cmcnews/NewsLogger.CMC/start.sh
#         break
#     else
#         echo Still on dw...
#         sleep 20m
#     fi
# done