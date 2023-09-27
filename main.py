import cmc  # api for cmc to get news
import os
from datetime import datetime
import time
import requests

# For MySQL database
import json
import pymysql
dbconf = json.loads(os.environ.get("MYSQL_DB1_JSON_CONN", ""))


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
if __name__ == '__main__':
    cmc_api = cmc.API()
    try:
        # Start service to get news
        cmc_api.start_service()
        send_ntfy("Program has started", f"{datetime.now()}", tags="computer")
        time.sleep(5)
        news = cmc_api.get_news()  # Get news

        # ! Print news to console and save to file  ---  BACKUP FOR REDUNDANCY
        print(f"Adding to (Backup) news folder...")
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

        print(f"Adding to database... in 5")
        time.sleep(5)
        # MySQL database setup
        connection = pymysql.connect(host=dbconf["host"], user=dbconf["user"],
                                     password=dbconf["password"], db=dbconf["database"],
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        # Add news to database
        for item in news:
            try:
                # Get time of news and convert to timestamp
                wanted_time = datetime.strptime(
                    item["datetime"], "%d.%m.%Y %H:%M")
                # Connect to database and insert news
                with connection.cursor() as cursor:
                    # SQL query to insert news, (newstime in correct format, stock, content)
                    sql = "INSERT INTO `newslogs` (`newstime`, `stock`, `content`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (
                        wanted_time.strftime('%Y-%m-%d %H:%M:%S'),
                        item["market"],
                        item["content"]))
            # If Error is for duplicate entry, skip
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:
                    print(str(item["datetime"]) + "Duplicate entry, skipping")
                    pass
                else:
                    raise e
            finally:
                connection.commit()  # Commit changes to database
        # Close connection to database after all news has been added
        connection.commit()
        connection.close()

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
