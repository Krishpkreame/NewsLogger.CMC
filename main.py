import cmc  # api for cmc to get news
import os
from datetime import datetime
import time
import requests


def send_ntfy(title, msg, tags="warning"):  # Send notification to my phone
    requests.post(
        "https://ntfy.sh/krish_patel_cmc_news_logger",  # Custom url for updates
        # Send date and time with message
        data=f"{msg}",
        headers={
            "Title": title,  # Title of notification
            "Tags": tags  # Adds a warning icon to the notification
        })


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
            print(item)
            # Filepath cleanup and formatting
            marketpath = item["market"].replace(" ", "_").lower()
            marketpath = "".join(
                [c for c in marketpath if c.isalpha() or c.isdigit() or c in ["_", "."]])

            filenamepath = item["title"].replace(
                " ", "_").lower() + "_" + item["datetime"]
            filenamepath = "".join(
                [b for b in filenamepath if b.isalpha() or b.isdigit() or b in ["_", "."]])

            filepath = f"./News/{marketpath}/{filenamepath}.txt"
            print(filepath)
            with open(filepath, "w") as f:  # Write content to file
                f.write(item["content"])

            # Set file modification time to the time of the news for sorting in file explorer
            wanted_time = datetime.strptime(
                item["datetime"], "%d.%m.%Y %H:%M").timestamp()
            os.utime(filepath, (wanted_time, wanted_time))

        send_ntfy(
            "News Updated", f"News has been updated\n{len(news)} new news item added", tags="tada")
        cmc_api.stop_service()  # Stop service after getting news
    except KeyboardInterrupt:
        send_ntfy("Debugging", "Keyboard Interrupt", tags="")
        cmc_api.stop_service()

    except Exception as e:
        send_ntfy("Error Occured", str(e))
        cmc_api.stop_service()
        raise e
