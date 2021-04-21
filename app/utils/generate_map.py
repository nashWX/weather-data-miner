from os import path, remove as removeFile
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from geopy.geocoders import Nominatim
from PIL import Image, ImageOps
from django.conf import settings


saveLocation = settings.BASE_DIR / 'static' / 'img' 
returnPath = ''
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42"

def generate_map(location_name='', location_id=''):
    #main acctual file location
    name = saveLocation/(location_id+'_map.png')
    #temp file location
    temp_path = saveLocation / 'temp.jpg'
    #this location will use for show this image in template
    returnPath = f'img/{location_id}_map.png'

    if not location_name and not location_id:
        return
    
    if path.exists(name):
        return  returnPath
    
    try:
        geolocator = Nominatim(user_agent=agent)
        locationz = geolocator.geocode(location_name)
        lons = locationz.longitude
        lats = locationz.latitude 
        m = Basemap(projection='merc',llcrnrlat=lats-2,urcrnrlat=lats+2,\
                    llcrnrlon=lons-4, urcrnrlon=lons+4, resolution='l', area_thresh=15)

        x,y = m(lons, lats)
        m.drawcoastlines(color='aqua', linewidth=1)
        m.drawcountries(color='aqua', linewidth=1)
        m.drawstates(color='aqua', linewidth=2)
        m.drawrivers(color='teal', linewidth=0.9)
        m.fillcontinents(color='black', lake_color='gray')
        m.drawlsmask(land_color='black', ocean_color='aqua', resolution='l')
        m.plot(x, y, 'ko', markersize=10.5)
        m.plot(x, y, 'wo', markersize=8)
        plt.savefig(temp_path, dpi=100, facecolor='b', edgecolor='b',
                orientation='portrait', format=None,
                transparent=False, bbox_inches=None, pad_inches=0.1)

        img = Image.open(temp_path) 
        border = (100, 100, 100, 100) # left, up, right, bottom
        cropped_img = ImageOps.crop(img, border)
       
        cropped_img.save(name, 'PNG')
        #removing temporary image
        removeFile(temp_path)

        return returnPath
    except Exception as e:
        print('error ', e)