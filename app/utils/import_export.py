import asyncio
import aiofiles
from asgiref.sync import sync_to_async
from django.conf import settings
from app.models import Location
# from instagramy import InstagramLocation
# from .InstaLocation import InstaLocation

async def exportToText():
    locations = await sync_to_async(Location.objects.all)()
    locations = await sync_to_async(list)(locations)
    print('export started')
    async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'locations_with_id.txt', 'w') as f:
        for loc in locations:
            line = ';'.join([loc.name,loc.location_id or '',loc.population or '',loc.city_name,loc.state_name,loc.lat,loc.lng])
            await f.write(line)
    print('location export complete')

async def exportOnlyId():
    async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'locations_with_id.txt', 'r') as f:
        async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'locations__id.txt', 'w') as f2:
            async for line in f:
                data = line.strip().split(';')
                await f2.write(data[1])
                await f2.write('\n')

    print('location_id export complete')

async def importFromText():
    async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'locations_with_id.txt', 'r') as f:
        i=0
        async for line in f:
            try:
                data = line.strip().split(';')
                loc,created = await sync_to_async(Location.objects.get_or_create)(
                    name=data[0],
                    location_id=data[1],
                    population=data[2],
                    city_name=data[3],
                    state_name=data[4],
                    lat=data[5],
                    lng=data[6]
                )
                if created:
                    await sync_to_async(loc.save)()
                    print(i)
                    i += 1
            except Exception as e:
                print(f'Import error {e}')


async def updateLocationFromTxt():
    async with aiofiles.open(settings.BASE_DIR/'static'/'check_files'/'verified-location.txt', 'r') as f:
        i=0
        async for line in f:
            try:
                data = line.strip().split(';')
                loc = await sync_to_async(Location.objects.filter)(
                    name__iexact=f"{data[1]}, {data[2]}",
                )

                loc =  await sync_to_async(loc.first)()

                if loc is None:
                    loc = await sync_to_async(Location.objects.create)(
                        city_name=data[1],
                        name=f"{data[1]}, {data[2]}",
                        state_name = data[2]
                    )
                loc.location_id = data[0]
                loc.lat = data[3]
                loc.lng = data[4]
                await sync_to_async(loc.save)()
                print(i)
                i += 1
            except Exception as e:
                print(f'Import error {e}')

def handleImport():
    asyncio.run(importFromText())

def handleExport():
    asyncio.run(exportToText())

def handleOnlyIdExport():
    asyncio.run(exportOnlyId())

def handleUpdateLocation():
    asyncio.run(updateLocationFromTxt())

if __name__ == "__main__":
    handleUpdateLocation()