from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from geopy.geocoders import Nominatim
# from PIL import Image 
# from PIL import ImageOps

from django.conf import settings

saveLocation = settings.BASE_DIR / 'media' / 'big_map' 
shapefile_path = settings.BASE_DIR / 'static/cb_2015_us_county_500k/cb_2015_us_county_500k'

def big_map(lats_bounds=None, lons_bounds=None, lats=None, lons=None, place_name=None, marker=False):
        Path(saveLocation).mkdir(parents=True, exist_ok=True)
        # # When address is given a "location, state" it generates a .png of the location
        # address= 'Fort Myers, Florida'
        # # print(address)
        # geolocator = Nominatim(user_agent="Your_Name")
        # locationz = geolocator.geocode(address)
        # lons = locationz.longitude
        # lats = locationz.latitude
        # lats_bounds = 25.5, 28
        # lons_bounds = -84, -79.2

        name = saveLocation/(place_name+'.png')

        #this location will use for show this image in template

        returnPath = f'/media/big_map/{place_name}.png'

        if Path(name).is_file():
                return  returnPath

        if lats_bounds is None or lons_bounds is None or lats is None or lons is None or place_name is None:
                return None

        m = Basemap(projection='merc',llcrnrlat=lats_bounds[0],urcrnrlat=lats_bounds[1],
                llcrnrlon=lons_bounds[0], urcrnrlon=lons_bounds[1], resolution='l', area_thresh=100)
        # m = Basemap(projection='merc',llcrnrlat=center[0]-2,urcrnrlat=center[0]+2,\
        #                 llcrnrlon=center[1]-4, urcrnrlon=center[1]+4, resolution='l', area_thresh=100)

        x,y = m(lons, lats)
        try:
            m.drawcoastlines(color='aqua', linewidth=1)
        except Exception as e:
            print(f'coastlines not found {e} ')
        # m.drawcoastlines(color='aqua', linewidth=1)
        m.drawcountries(color='aqua', linewidth=1)
        m.drawstates(color='aqua', linewidth=2)
        m.drawrivers(color='teal', linewidth=0.9)
        m.fillcontinents(color='black', lake_color='gray')
        m.drawlsmask(land_color='black', ocean_color='aqua', resolution='l')
        m.readshapefile(str(shapefile_path),'counties',drawbounds=True,color='aqua')
        # m.readshapefile("F:/workspace/django/weatherapp/weather/static/virginia/vr",'counties',drawbounds=True,color='aqua')
        if marker:
                m.plot(x, y, 'ko', markersize=6.5)
                m.plot(x, y, 'wo', markersize=4)

        try:
                plt.axis('off')
                plt.gca().set_axis_off()
                plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                        hspace = 0, wspace = 0)
                plt.margins(0,0)
                plt.gca().xaxis.set_major_locator(plt.NullLocator())
                plt.gca().yaxis.set_major_locator(plt.NullLocator())

                plt.savefig(saveLocation/place_name, dpi=100, facecolor='b', edgecolor='b',
                orientation='portrait', format=None,
                transparent=True, bbox_inches='tight', pad_inches=0)

                return returnPath
        except Exception as e:
                print(e)


if __name__ == '__main__':
        big_map(lats_bounds=(25.5, 28), lons_bounds=(-84, -79.2),  lats=26.640628, lons=81.8723084, place_name='florida')