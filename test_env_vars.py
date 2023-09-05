# Testing environment variables
import os

# use export on linux or mac to set environment variables
print(os.environ.get("SELENIUM_URL", "failed"))
