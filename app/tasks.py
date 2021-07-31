import asyncio
from celery import shared_task
from .models import Location
from .utils.get_hashtag import get_hashtag
from .utils.retrive_warnings import retrieveWarnings
from .utils.generate_map import generate_map


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
            mapPath = generate_map(float(location.lat), float(location.lng), location.location_id)
            location.location_map = mapPath
            location.save()
    except Exception as e:
        print(f'got this exception {e}')



@shared_task
def update_hash_tag(name):
    asyncio.run(get_hashtag(name))