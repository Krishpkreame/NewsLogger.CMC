import requests
from datetime import datetime
import os


def send_notification(title, msg=datetime.now(), tags="warning"):
    # Get url from environment variable
    url = os.environ.get("NTFY_URL", "")
    # Check if url is set
    if not url:
        raise Exception("NTFY_URL environment variable not set")

    # Send notification to my phone
    requests.post(
        url,  # Custom url for updates
        data=f"{msg}",  # Set msg
        headers={
            "Title": title,  # Title of notification
            "Tags": tags  # Adds an icon to the notification
        })
