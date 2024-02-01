#!/bin/bash

# Infinite loop
while true; do
    # Get the current hour in 24-hour format
    current_hour=$(date +%H)
    echo "Current hour: $current_hour"

    # Check if the current hour is 02 (2 AM)
    if [ "$current_hour" -eq 13 ]; then
        # Execute your Python script here
        python ./main.py
        sleep 5400 # Sleep for 1.5 hours (5400 seconds)

    fi

    # Sleep for some time (for example, 1 hour) and check again
    echo "Sleeping for 1 hour"
    sleep 1800 # Sleep for 30mins (1800 seconds)
done
