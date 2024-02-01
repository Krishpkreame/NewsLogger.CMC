import cmc
import ntfy
from exceptions import *
import os
from datetime import datetime
import time
import json
import pymysql


# This is a test file to see if the api works and saves as txt files.
if __name__ == '__main__':
    try:
        dbconfig = json.loads(os.environ.get("MYSQL_DB1_JSON_CONN", ""))
        if not dbconfig:
            ntfy.send_notification(
                "Database Config Not Found", tags="no_entry")
            raise EnvironmentVariableNotFound(
                "MYSQL_DB1_JSON_CONN environment variable not set")

        connection = pymysql.connect(
            host=dbconfig["host"], user=dbconfig["user"],
            password=dbconfig["password"], db=dbconfig["database"],
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            sql = "SELECT * FROM `input_info`"
            cursor.execute(sql)
            dbkeywords = [row['cmc_keyword'] for row in cursor]
        if not dbkeywords:
            ntfy.send_notification("No keywords found", tags="no_entry")
            raise DatabaseError("Could not find keywords in database")

        cmc_api = cmc.API()  # New cmc instance with keywords
        cmc_api.set_keywords(dbkeywords)  # Set keywords from database
        cmc_api.start_service()  # Start service to get news
        time.sleep(3)
        ntfy.send_notification("Program has starting", tags="computer")
        news = cmc_api.get_news()  # Get news
        time.sleep(3)
        cmc_api.stop_service()  # Stop service

        if not news:
            raise CMCError("No news found")

        print(f"Adding to database... in 5")
        time.sleep(5)

        # Add news to database
        for artical in news:
            # Get time of news and convert to timestamp
            wanted_time = datetime.strptime(
                artical["datetime"], "%d.%m.%Y %H:%M")
            try:
                # Connect to database and insert news
                with connection.cursor() as cursor:
                    # SQL query to insert news, (newstime in correct format, stock, content)
                    sql = "INSERT INTO `newslogs` (`newstime`, `stock`, `content`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (
                        wanted_time.strftime('%Y-%m-%d %H:%M:%S'),
                        artical["market"],
                        artical["content"]))
            # If Error is for duplicate entry, skip
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:
                    print(f"{str(artical['datetime'])} Duplicate entry")
                    pass
                else:
                    raise e
            finally:
                connection.commit()  # Commit changes to database
        # Close connection to database after all news has been added
        connection.commit()
        connection.close()
    except BaseException as e:
        ntfy.send_notification("Error Occured", str(e))
        if cmc_api.cmc_started:
            cmc_api.stop_service()
        raise e
