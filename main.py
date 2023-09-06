import cmc  # api for cmc to get news
import os
from datetime import datetime
import time

# This is a test file to see if the api works and saves as txt files.
# TODO - Use Database for saving news

if __name__ == '__main__':
    cmc_api = cmc.API()
    try:
        cmc_api.start_service()  # Start service to get news
        time.sleep(5)
        news = cmc_api.get_news()  # Get news

        # Print news to console and save to file
        for item in news:
            print("--------------------------------------------------")
            print("_____", end="")
            print(item["datetime"])
            print("_____", end="")
            print(item["title"])
            print("_____", end="")
            print(item["content"])
            print()

            # Filepath cleanup and formatting
            filepath = ''.join(
                char for char in f"{item['title']}_____{item['datetime']}" if char.isalnum() or char in [" ", ".", "_"])
            filepath = f"./News/{filepath}.txt"

            with open(filepath, "w") as f:  # Write content to file
                f.write(item["content"])

            # Set file modification time to the time of the news for sorting in file explorer
            wanted_time = datetime.strptime(
                item["datetime"], "%d.%m.%Y %H:%M").timestamp()
            os.utime(filepath, (wanted_time, wanted_time))

        cmc_api.stop_service()  # Stop service after getting news

    except BaseException as e:
        print(e)
        cmc_api.stop_service()
