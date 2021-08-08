import asyncio
from pyppeteer import launch
from asgiref.sync import sync_to_async
from ..models import Warning
from .helpers import (
    userAgent,
    login,
    get_location
)

async def update_location():
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

    try:
        page = await browser.newPage()
        await page.setUserAgent(userAgent)
        await login(page, 'islamahsan62')
        warnings = await sync_to_async(Warning.objects.select_related)('location')
        warnings = await sync_to_async(warnings.filter)(location__location_id__isnull=True)
        warnings = await sync_to_async(warnings.order_by)('-id')
        warningList = await sync_to_async(list)(warnings)
        for warning in warningList[:20]:
            try:
                place_data = await get_location(warning.location.name, page)
                if place_data:
                    print(place_data['location']['facebook_places_id'])
                    warning.location.location_id = f"{place_data['location']['facebook_places_id']}"
                    await sync_to_async(warning.location.save)()
            except Exception as e:
                print("error ", e)
    except Exception as e:
        print(f'Exception fetching missing location id')

    await page.close()
    await browser.close()


def main():
    asyncio.run(update_location())

if __name__ == "__main__":
    asyncio.run(update_location())