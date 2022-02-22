import requests
from time import sleep

async def make_request(url):
    for i in range(3):
        try:
            r = requests.get(url, timeout = 6)
            if r.status_code == 200:
                return (True, r)
        except requests.exceptions.Timeout:
            print ("The API didn't respond (Attempt #{}).".format(i+1))
        if i < 2:
            print ("Trying again...")
            sleep(1)
    await ctx.send("We couldn't fetch the data from the API. Please try again later!", hidden = True)
    return (False, None)   