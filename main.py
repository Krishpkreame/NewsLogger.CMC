import cmc  # api for cmc to get news
import os
from datetime import datetime
import time

if __name__ == '__main__':
    cmc_api = cmc.API()
    try:
        cmc_api.start_service()
        time.sleep(5)
        news = cmc_api.get_news()

        for item in news:
            print("--------------------------------------------------")
            print(item["datetime"])
            print(item["title"])
            print(item["content"].split("\n")[2:-2])

            filepath = ''.join(
                char for char in f"{item['title']}...{item['datetime']}" if char.isalnum() or char == '.' or char == ' ')
            filepath = f"./News/{filepath}.txt"

            with open(filepath, "w") as f:
                f.write(item["content"])
                f.close()

            wanted_time = datetime.strptime(
                item["datetime"], "%d.%m.%Y %H:%M").timestamp()

            os.utime(filepath, (wanted_time, wanted_time))

        input("DONE")
        cmc_api.stop_service()  # ! ------------------->

    except BaseException as e:
        print(e)
        cmc_api.stop_service()
