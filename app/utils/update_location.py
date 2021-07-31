import asyncio
from pyppeteer import launch
from pathlib import Path
from asgiref.sync import sync_to_async
from ..models import Location, Warning
from .helpers import (
    userAgent,
    login,
    get_population,
    get_location
)

async def update_location(places: list = [], warning_type: str = ""):
    browser = await launch({
        "headless": True,
         'args': [
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--no-sandbox',
            '--no-zygote',
            '--deterministic-fetch',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials',
            #'--single-process',
        ],
    })
    page = await browser.newPage()
    await page.setUserAgent(userAgent)
    await login(page)
    warnings = await sync_to_async(Warning.objects.filter)(warning_type=warning_type)
    await sync_to_async(warnings.delete)()

    for place in places:
        try:
            name = place[0] + ", " + place[1]
            start_time = place[2]
            end_time = place[3]
            loc = None
            result = await sync_to_async(Location.objects.filter)(name=name)
            if not await sync_to_async(result.exists)():
                place_data = await get_location(name, page)
                if place_data:
                    location = Location(name=name, city_name=place[0], state_name=place[1])
                    location.location_id = f"{place_data['location']['facebook_places_id']}"
                    location.lng = f"{place_data['location']['lng']}"
                    location.lat = f"{place_data['location']['lat']}"
                    location.population = await get_population(name, page)
                    await sync_to_async(location.save)()
                    loc = location
            else:
                loc = result[0]

            if loc:
                await sync_to_async(Warning.objects.create)(
                    location=loc,
                    start_time=start_time,
                    end_time=end_time,
                    warning_type=warning_type,
                )
 
        except Exception as e:
            print("error ", e)
    await page.close()
    await browser.close()


if __name__ == "__main__":
    asyncio.run(update_location())