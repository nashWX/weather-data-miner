import matplotlib

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from django.conf import settings
from pathlib import Path

matplotlib.use('Agg')

saveLocation = settings.BASE_DIR / 'media' / 'img' 
returnPath = ''
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42"


def generate_map(lats=None, lons=None, place_id=None, withMarker=True, points=None, width=None, height=None):

    #create new directory if not exists
    Path(saveLocation).mkdir(parents=True, exist_ok=True)

    if not place_id and not points:
        place_id = str(str(f"{lats}_{lons}").__hash__())

    if not place_id and points and not len(points[0]) and not len(points[1]):
        place_id = str(str(f"{lats}_{lons}").__hash__())
    
    if not place_id and points:
        place_id = str(str(points).__hash__())
    
    #main acctual file location
    name = saveLocation/(place_id+'_map.png')

    #this location will use for show this image in template

    returnPath = f'/media/img/{place_id}_map.png'

    # if not location_name and not location_id:
    #     return
    if not lats and not lons and not place_id:
        return
    
    if Path(name).is_file():
        return  returnPath
    
    try:
        m = None
        if width and height:
            latbox1=lats-width
            latbox2=lats+width
            lonbox1=lons-height
            lonbox2=lons+height
            m = Basemap(projection='merc',llcrnrlat=latbox1,urcrnrlat=latbox2,\
                llcrnrlon=lonbox1, urcrnrlon=lonbox2, resolution='l', area_thresh=15)
        else:
            m = Basemap(projection='merc',llcrnrlat=lats-2,urcrnrlat=lats+2,\
                        llcrnrlon=lons-4, urcrnrlon=lons+4, resolution='l', area_thresh=100)

        x,y = m(lons, lats)

        if points:
            x,y = m(points[1], points[0])

        try:
            m.drawcoastlines(color='aqua', linewidth=1)
        except Exception as e:
            print(f'coastlines not found {e} ')
        m.drawcountries(color='aqua', linewidth=1)
        m.drawstates(color='aqua', linewidth=2)
        m.drawrivers(color='teal', linewidth=0.9)
        m.fillcontinents(color='black', lake_color='gray')
        m.drawlsmask(land_color='black', ocean_color='aqua', resolution='l')

        if withMarker:
            if points:
                m.plot(x, y, 'ko', markersize=6.5)
                m.plot(x, y, 'wo', markersize=4)
            else:
                m.plot(x, y, 'ko', markersize=10.5)
                m.plot(x, y, 'wo', markersize=8)

        plt.axis('off')
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                    hspace = 0, wspace = 0)
        plt.margins(0,0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        plt.savefig(name, dpi=100, facecolor='b', edgecolor='b',
                orientation='portrait', format=None,
                transparent=True, bbox_inches='tight', pad_inches=0)

        plt.close('all')

        return returnPath
    except Exception as e:
        print('error ', e)
        return None
