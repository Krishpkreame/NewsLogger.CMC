import cmc
import os
import time

if __name__ == '__main__':
    cmc_api = cmc.API()
    cmc_api.start_service()
    time.sleep(5)
    print("DONE")
