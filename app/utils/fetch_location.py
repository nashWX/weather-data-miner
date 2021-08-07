import asyncio
import os
from pyppeteer import launch
import aiofiles
import django
django.setup()
from asgiref.sync import sync_to_async
from django.conf import settings
from .helpers import userAgent
from app.models import Location
from django.db.models import Q
from aiomultiprocess import Pool


async def fetchLocation(link):
    browser = await launch({
        'args': [
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-first-run',
            # '--no-sandbox',
            '--no-zygote',
            '--deterministic-fetch',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials',
            #'--single-process',
        ]})
    page = await browser.newPage()
    await page.setUserAgent(userAgent)

    # async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'instagram_cities_link.txt') as f:
    #     async for link in f:
    try:
        link = link.strip()
        print('current link ', link)
        await page.goto(link, {"waitUntil": "networkidle0"})
        data = await page.evaluate("""async() => {
            let pagination = document.querySelector('main > div > a');
            let data = [];
            let i = 0;
            while(i < 15) {
                i++;
                if(pagination) {
                    pagination.click()
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
                pagination = document.querySelector('main > div > a');
            }

            const allLinks = document.querySelectorAll('main div ul > li > a');
            if(allLinks && allLinks.length) {
                for(let link of allLinks) {
                    data.push({
                        name: link.textContent,
                        id: link.href.split('/')[5]
                    });
                }
            }

            return data;
        }""")

        for item in data:
            name = item['name']
            filters = await sync_to_async(Location.objects.filter)(Q(city_name__icontains=name) | Q(name__icontains=name), location_id=None)
            loc = await sync_to_async(filters.first)()
            if loc:
                loc.location_id = item['id']
                await sync_to_async(loc.save)()
                print(f'{item["name"]} -> {item["id"]}')
    except Exception as e:
        print(e)
    
    try:
        if page.isClosed() is False:
            print('page closing...')
        await page.close()
        await browser.close()
    except Exception as e:
        print(f'closing exceptin {e}')
        await browser.close()

    return link


async def multi():
    async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'instagram_cities_link.txt') as f:
        links = await f.read()
        for chunk in chunks(links.splitlines(), 3):
            print('-----------------------------')
            async with Pool() as pool:
                async for result in pool.map(fetchLocation, chunk):
                    print(f'completed {result}')
            try:
                os.system('taskkill.exe /F /im Chrome.exe')
            except Exception as e:
                print(f'kill exception {e}')
            

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main():
    asyncio.run(multi())
