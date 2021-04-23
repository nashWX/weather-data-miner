from .data import locations, location_url
from .generate_map import generate_map

def get_locations():
    for location in locations:
        if type(location.get('name')) is str:
            location['name'] = location.get('name').split(',')
            print("location ", location)
        location['location_map'] = generate_map(location.get('name'), location.get('location_id'))

    return locations
