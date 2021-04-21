from .data import locations, location_url
from .generate_map import generate_map

def get_locations():
    for location in locations:
        location['location_map'] = generate_map(location.get('name'), location.get('location_id'))

    return locations
