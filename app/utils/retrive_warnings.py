import re
import os
from app.models import Location, Warning
import pytz
import asyncio
import datetime as dt
from django.conf import settings
from asgiref.sync import sync_to_async
import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
from dateutil.tz import UTC

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

filePath = settings.BASE_DIR / 'static' / 'check_files'

async def retrieveWarnings(event='TORNADO'):
    warning_type = 'Tornado Warning'
    split_by = 'Tornado Warning for...'

    if event == 'FLOOD':
        warning_type = 'Flash Flood Warning'
        split_by='Flash Flood Warning for...'
    if event == 'TSTORM':
        warning_type = 'Severe Thunderstorm Warning'
        split_by = 'Severe Thunderstorm Warning for...'
    
    URL = f'https://api.weather.gov/alerts/?event={warning_type}'
    # Load US states
    us_states = {}
    async with aiofiles.open(filePath/'us_states.txt') as f:
        async for line in f:
            (key,val) = line.split(',')
            us_states[key] = val.strip()

    # 1. Scrape the national weather service API for tornado warnings.
    tornadowarnings = []
    async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
        async with session.get(URL) as resp:
            if resp.status != 200:
                print("Request failed, API site likely down for maitenance.")
                print("Try again later. Status code: {0}".format(resp.status))
            else:
                a = await resp.json()
                tornadowarnings = a['features']
    # Loop through every warning.
    given_tornado_places = []
    for warning in tornadowarnings:
        if not warning['properties']['messageType']=='Alert':
            continue # Not interested in updates or cancels, just alerts.
        # 2. Get warning times, given in local time so need to convert to UTC
        if not warning['properties']['effective'] or not warning['properties']['ends']:
            continue
        
        warningStart = warning['properties']['effective']
        warningEnd = warning['properties']['ends']
        warning_start = local_to_UTC(warningStart)
        warning_end = local_to_UTC(warningEnd)
        current_time =  dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=1)
        warning_delete_end =  dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=2)
  
       
        if current_time > warning_end:
            continue        
        
        # 3. Retrieve ifno from warning. 
        # County info returns string: County1, State ID1; County2, StateID2 etc 
        county = warning['properties']['areaDesc']
        # Description is the text that is displayed on the web
        warning_text = warning['properties']['description']
        #print(warning_text)
        
        # 4. Retrieve all possible places.
        # One feature of the descriptions is that locations are only mentioned
        # after "Tornado Warning for...", can get rid of everything before this.
        # Also replace linebreaks with spaces, necessary for the regex in 
        # situations where a place name spans to lines.
        warning_text_split = warning_text.split(split_by,1)

        if len(warning_text_split) > 1:
            location_text = warning_text_split[1].replace("\n"," ")
        else:
            location_text = warning_text_split[0].replace("\n"," ")
        # Use regex to find possible places. The format should be
        #  - Preceded by a space (or linebreak as theses are now spaces), gets 
        #      rid of some unneccessary words.
        #  - Start with a capital followed by a number of lower case letters.
        #  - Possibly followed by a dot (i.e. St.)
        #  - Possible followed by a space or dash followed by the same format 
        #      again.
        poss_places = re.findall(r' [A-Z]+[a-z]+[\.]?[ \-]?(?:[A-Z]+[a-z]+[ ]?)*',
                                 location_text)
        # 5. Reduce place list - the tricky part!
        places = []
        for place in poss_places:
            if await check_place(place,county,us_states):         
                places.append(place.strip().strip('.').replace("St. ","Saint "))
        # 5.5 Look for duplicates
        places = list(set(places))
    
        # 6 Create list:
        state_abbr = county.split(';')[0].split(',')[1].strip()
        state = [k for k,v in us_states.items() if v == state_abbr]
        # startTimeStr = warning_start.strftime("%Y%m%d%H%M")
        # endTimeStr = warning_end.strftime("%Y%m%d%H%M")
        warnings = await sync_to_async(Warning.objects.filter)(warning_type=event, end_time__lte=warning_delete_end)
        await sync_to_async(warnings.delete)()
        for p in places:
            # place_dets = [p,state[0],warning_start,warning_end]
            # given_tornado_places.append(place_dets)
            filters = await sync_to_async(Location.objects.filter)(city_name__iexact=p, state_name__iexact=state[0])
            location = await sync_to_async(filters.first)()
            if location:
                obj, created = await sync_to_async(Warning.objects.get_or_create)(
                    location=location,
                    start_time=warning_start,
                    end_time=warning_end,
                    warning_type=event,
                )
                if created:
                    print(f'{location} -> {warning_start} -> {warning_end}')
                    await sync_to_async(obj.save)()
    
        
        
     
       
        

    
async def check_place(place, counties,us_states):
    '''
    Series of checks on a place name to reduce the place list to just locations
    we are interested in. 
    I have ordered this list to avoid constantly scraping the web for place 
    names.
    If false then the retrieveWarnings() will just continue to the next place
    in the list.
    If True then the place name will be noted.
    '''
    place = place.strip().lower().strip('.')
    filters = await sync_to_async(Location.objects.filter)(city_name__icontains=place, name__icontains=place)
    if await sync_to_async(filters.exists)():
        return True
    else:
        return False



async def get_place_list(county_list,state_list):
    ''' Get all places in a list of counties according to geographic.org'''
    all_places = []
    for county, state in zip(county_list, state_list):
        places = await scrape_geographic(state,county)
        all_places = all_places + places
    return all_places
    
async def scrape_geographic(state,county):
    ''' Retrieve a list of all places in a county according to geographic.org
    '''
    url = 'https://geographic.org/streetview/usa/' + \
        '{0}/{1}/index.html'.format(state.lower(),county.lower())
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()

    soup = BeautifulSoup(text,'html.parser')
    places = soup.find_all('li')
    place_list = []
    for place in places:
        place_list.append(place.get_text())
    return place_list
        
async def scrape_wiki(state):
    ''' Retrieve a list of all census designated places in a state according 
    to wikipedia.'''
    base_url = 'https://en.wikipedia.org/wiki/'
    url = base_url + 'List_of_census-designated_places_in_' +\
    '{0}'.format(state.title().strip().replace(' ','_'))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
    soup = BeautifulSoup(text,'html.parser')
    places = soup.find_all('li')
    place_list = []
    for place in places:
        place_list.append(place.get_text())
    return place_list

def local_to_UTC(time_string):
    # Converts a time string given in the format of 
    # YYYY-mm-ddTHH:MM:SS+/-H*H*, where the +/- is the difference to UTC
    # Currently assumes that it is a time that is behind UTC.
    # time = dt.datetime.strptime(time_string[0:19],"%Y-%m-%dT%H:%M:%S")
    # utcdiff = time_string[19:22]
    # utctime = time + dt.timedelta(hours=int(utcdiff))
    # return pytz.utc.localize(utctime)
    dt = isoparse(time_string)
    return dt.astimezone(UTC)




def main():
    asyncio.run(retrieveWarnings('TSTORM'))
    
if __name__=='__main__':
    main()
    