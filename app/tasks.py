import asyncio
from asyncio.runners import run
from celery import shared_task
from pyppeteer import launch
from django.db.models import Q
from asgiref.sync import sync_to_async
from .models import Location
from .utils.update_location import update_location
from .utils.get_hashtag import get_hashtag
from .utils.retrive_warnings import retrieveWarnings
from .utils.generate_map import generate_map
from .utils.helpers import (
    userAgent,
    get_population_from_wiki
)
@shared_task
def tornadow_warning():
    asyncio.run(retrieveWarnings(event='TORNADO'))


@shared_task
def thunderstorm_warning():
    asyncio.run(retrieveWarnings(event='TSTORM'))

@shared_task
def flood_warning():
    asyncio.run(retrieveWarnings(event='FLOOD'))

@shared_task
def update_location_map(id:int):
    try:
        location = Location.objects.get(id=id)
        if not location.location_map:
            mapPath = generate_map(float(location.lat), float(location.lng), location.location_id or '_'.join(location.name.lower().split(',')))
            location.location_map = mapPath
            location.save()
    except Exception as e:
        print(f'got this exception {e}')


@shared_task
def update_empty_map():
    try:
        locations = Location.objects.filter(location_map__isnull=True, lat__isnull=False, lng__isnull=False)
        for location in locations:
            if not location.location_map:
                mapPath = generate_map(float(location.lat), float(location.lng), location.location_id or '_'.join(location.name.lower().split(',')))
                location.location_map = mapPath
                location.save()
    except Exception as e:
        print(f'got this exception {e}')


@shared_task
def update_population():
    asyncio.run(update_missing_pouplation())


@shared_task
def update_hash_tag():
    asyncio.run(get_hashtag())

@shared_task
def update_missing_location_id():
    try:
        asyncio.run(update_location())
    except Exception as e:
        print(f'update_location error {e}')

async def update_missing_pouplation():
    try:
        browser = await launch({'args': [
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--no-sandbox',
            '--no-zygote',
            '--deterministic-fetch',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials'],
        })
        page = await browser.newPage()
        await page.setUserAgent(userAgent)
        locations = await sync_to_async(Location.objects.filter)((Q(population__isnull=True) | Q(population='') & Q(can_retrive_population=True)))

        for location in locations[:100]:
            population = await get_population_from_wiki(location.name, page)
            location.population = population
            location.can_retrive_population = False
            await sync_to_async(location.save)()
    except Exception as e:
        print(f'failed updated population from wikipedia {e}')

    await page.close()
    await browser.close()