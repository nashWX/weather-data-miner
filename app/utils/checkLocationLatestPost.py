import requests
import random
# from django.conf import settings
from tqdm import tqdm
import concurrent.futures
import numpy as np
import random
user_agents = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.googlebot.com/bot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
]


def checkPostExistsOnThisLocation(warning=None, timestamp=0):
    url = f"https://www.instagram.com/explore/locations/{warning.location.location_id}/?__a=1"
    headers = {"user-agent": random.choice(user_agents)}
    cookies = {"sessionid": "4526877383%3ACd5ZxBHdghkgPp%3A17"}
    proxies={
        # "http": "http://ylnmpdzr-rotate:fcyzrvj2mpa3@p.webshare.io:80/",
        # "https": "http://ylnmpdzr-rotate:fcyzrvj2mpa3@p.webshare.io:80/"
        "http": "http://qugpmcee-rotate:9quzip0643oo@p.webshare.io:80/",
        "https": "http://qugpmcee-rotate:9quzip0643oo@p.webshare.io:80/"
    }

    try:
        resp = requests.get(url, proxies=proxies, headers=headers, cookies=cookies)
        if resp.status_code != 200:
            raise Exception('unable to fetch location information')
        data = resp.json()
        recentPost = data['native_location_data']['recent']['sections'][0]['layout_content']['medias'][0]['media']
        post_time = recentPost['taken_at']
        print(post_time)
        if post_time >= timestamp:
            return True
        return None
    except Exception as e:
        #check error here
        print(e)
        pass
    return False


def checkPool(warnings=[], start_time=0):
    success_results = []
    failed_results = []
    for warning in warnings:
        success = checkPostExistsOnThisLocation(warning, start_time)
        if success == True:
            success_results.append(warning)
        elif success == False:
            failed_results.append(warning)

    return success_results, failed_results



def runThreading(chunks=[], numberOfThread=25, start_time=0, retry=1, results=[]):
    failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=numberOfThread) as executor:
        execList = []
        for chunk in chunks:
            execList.append(executor.submit(checkPool, chunk, start_time))
        
        for item in concurrent.futures.as_completed(execList):
            success_ids, failed_ids = item.result()

            if(len(success_ids)):
                results.append(success_ids)

            if(len(failed_ids)):
                failed.append(failed_ids)
    
    retry +=1
    if len(failed) and retry <= 2:
        return runThreading(failed, numberOfThread, start_time, retry, results)
    
    return results


def filterWarningByPost(queryset=[], start_time=0):
    # print(settings.BASE_DIR)
    # filePath = settings.BASE_DIR / 'static' / 'check_files' /  'locations__id.txt'
    # filePath2 = 'F:/workspace/django/weatherapp/weather/static/check_files/locations__id.txt'

    # filteredId = []
    # with open(filePath2, 'r') as f:
    #     data = f.readlines()
    #     for id in data:
    #         id = id.strip().strip('\n')
    #         if id:
    #             filteredId.append(id)

    filteredWarning = [warning for warning in queryset if warning.location.location_id]
    number_split = 20
    arr = np.array(filteredWarning)
    chunks = np.array_split(arr, number_split)
    results = runThreading(chunks, number_split, start_time)
    print(results)
    

    return [item for result in results for item in result]
        