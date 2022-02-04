from datetime import datetime
import json
import pytz
import os
from django.db.models import Q
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.core.cache import cache
from decouple import config
import celery
from app.utils.checkLocationLatestPost import filterWarningByPost

cache_timeout = 60 * 180


class AccessPassword(models.Model):

    class CoordinateType(models.TextChoices):
        MULTI_POLYGON = 'MultiPolygon', 'MultiPolygon'
        POLYGON = 'Polygon', 'Polygon',
        POINT = 'Point', 'Point'

    password = models.CharField(verbose_name="Access Password", max_length=12)
    name = models.CharField(max_length=255, verbose_name='User Name', blank=True, null=True)
    coordinates = models.JSONField(verbose_name='Location Coordinates', null=True)
    lat = models.FloatField(verbose_name='Latitude center of coordinates', max_length=24, null=True)
    long = models.FloatField(verbose_name='Longitude center of coordinates', max_length=24, null=True)
    coordinate_type = models.CharField(
        max_length=20,
        choices=CoordinateType.choices,
        default=CoordinateType.MULTI_POLYGON,
        verbose_name='Coordinate Type'
    )
    nearby_locations = models.JSONField(null=True, blank=True, verbose_name='All the locations inside the coordinates')

    @property
    def locations(self):
        if self.nearby_locations:
            return json.loads(self.nearby_locations)
        return []
    
    def __str__(self) -> str:
        return str(self.name)


class Util(models.Model):
    verify_media_url = models.URLField(verbose_name='Verify media url', null=True, blank=True)
    insta_sessionid = models.TextField(max_length=512, verbose_name='Instagram Session Id', help_text='Insert instagram sessionid separated by comma', null=True, blank=True)
    about_text = models.TextField(verbose_name='About Text', null=True, blank=True)
    turn_on_filtering = models.BooleanField(verbose_name='Turn on Post filtering', default=False)

class Location(models.Model):
    states = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "District of Columbia": "DC",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
    }
    name = models.CharField(
        verbose_name="Location name",
        max_length=255,
        null=False,
        unique=True,
        blank=False,
    )
    city_name = models.CharField(
        verbose_name="City Name", max_length=300, null=True, blank=False
    )
    state_name = models.CharField(
        verbose_name="State Name", max_length=300, null=True, blank=False
    )
    population = models.CharField(
        verbose_name="Population", max_length=255, null=True, blank=False
    )
    location_id = models.CharField(
        verbose_name="Location id", max_length=100, null=True, blank=False
    )
    location_map = models.CharField(
        verbose_name="Location map", max_length=300, null=True
    )
    lat = models.FloatField(
        verbose_name="Latitude", null=True, max_length=50, blank=True
    )
    lng = models.FloatField(
        verbose_name="Longitude", null=True, max_length=50, blank=True
    )
    can_retrive_population = models.BooleanField(
        verbose_name="can retrive population", default=True
    )

    def __str__(self):
        return self.name

    @property
    def small(self):
        name = f"{self.city_name}, {self.states.get(self.state_name, self.state_name[0]+self.state_name[-1])}"
        return name

    @property
    def popu(self):
        if self.population and self.population.isdigit():
            return f"{int(self.population):,}"
        return "UNKNOWN"

    @property
    def insta_url(self):
        return f"https://www.instagram.com/explore/locations/{self.location_id}"



class Warning(models.Model):
    timezone = config("timezone", default="America/New_York", cast=str)

    class WarningType(models.TextChoices):
        TORNADO = "TORNADO", "Tornado"
        FLOOD = (
            "FLOOD",
            "Flood",
        )
        TSTORM = (
            "TSTORM",
            "Thunderstorm",
        )

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="warnings"
    )
    start_time = models.DateTimeField(
        verbose_name="Warning start time.", null=True, blank=False
    )
    end_time = models.DateTimeField(
        verbose_name="Warning end time.", null=True, blank=False
    )
    warning_type = models.CharField(
        max_length=20,
        choices=WarningType.choices,
        default=WarningType.TORNADO,
    )

    def __str__(self) -> str:
        start = timezone.localtime(self.start_time, pytz.timezone(self.timezone))
        end = timezone.localtime(self.end_time, pytz.timezone(self.timezone))
        return f"{self.warning_type}, {start.strftime('%Y-%m-%d %I:%M %p')} <> {end.strftime('%Y-%m-%d %I:%M %p')}"

    @property
    def start(self):
        if self.start_time:
            local_dt = timezone.localtime(self.start_time, pytz.timezone(self.timezone))
            if os.name != 'nt':
                return f'{local_dt.strftime("%-I:%M")}<p>{local_dt.strftime("%p")}</p>'
            else:
                return f'{local_dt.strftime("%#I:%M")}<p>{local_dt.strftime("%p")}</p>'
        return None

    @property
    def end(self):
        if self.end_time:
            local_dt = timezone.localtime(self.end_time, pytz.timezone(self.timezone))
            if os.name != 'nt':
                return f'{local_dt.strftime("%-I:%M")}<p>{local_dt.strftime("%p")}</p>'
            else:
                return f'{local_dt.strftime("%#I:%M")}<p>{local_dt.strftime("%p")}</p>'
        return None

    @property
    def iso_start(self):
        return self.start_time.isoformat()

    @property
    def iso_end(self):
        return self.end_time.isoformat()

    @property
    def local_start(self):
        start = timezone.localtime(self.start_time, pytz.timezone(self.timezone))
        return start.strftime("%Y-%m-%d %I:%M")

    @property
    def local_end(self):
        end = timezone.localtime(self.end_time, pytz.timezone(self.timezone))
        return end.strftime("%Y-%m-%d %I:%M")

    @staticmethod
    def get_recent_warnings(_type="TORNADO"):
        latest_warnings = Warning.objects.filter(warning_type=_type).order_by(
            "-start_time"
        )
        warnings = []
        count = 0
        for latest_warning in latest_warnings:
            if all(
                [
                    latest_warning.start_time != warning.start_time
                    and latest_warning.end_time > warning.start_time
                    for warning in warnings
                ]
            ):
                warnings.append(latest_warning)
                count += 1
            if count >= 10:
                break

        warning_suggestions = []
        for i in range(0, len(warnings)):
            if len(warnings) > 1 and i < len(warnings) / 2:
                warning_suggestions.append(
                    {"start": warnings[i], "end": warnings[len(warnings) - (i + 1)]}
                )
            if len(warnings) == 1:
                warning_suggestions.append({"start": warnings[0], "end": warnings[0]})

        return warning_suggestions
    
    @staticmethod
    def get_warnings(_type='TORNADO', start_time=None, end_time=None, user=None):
        q = Q(warning_type=_type) & (Q(start_time__gte=start_time) & Q(end_time__lte=end_time)) & Q(location__id__in=user.locations) & Q(location__location_id__isnull=False)
        warnings = Warning.objects.select_related('location').filter(q).order_by('-start_time')
        key = str(warnings).__hash__()
        if cache.get(key):
            return cache.get(key)

        util = Util.objects.first()

        if warnings and util.turn_on_filtering and util.insta_sessionid:
            warnings = filterWarningByPost(warnings, datetime.timestamp(start_time))
            cache.set(key, warnings, cache_timeout)
        else:
            cache.set(key, warnings, cache_timeout)
        
        return warnings
    
    @property
    def formated(self):
        return {
            "warning_type": self.warning_type.lower(),
            "start": self.start,
            "end": self.end,
            "location": {
                "name": self.location.small[:20],
                "popu": self.location.popu,
                "location_map": self.location.location_map,
                "insta_url": self.location.insta_url,
            }
        }



class HashTag(models.Model):
    name = models.CharField(
        verbose_name="Tag Name",
        max_length=255,
        null=False,
        unique=True,
        blank=False,
    )
    post = models.CharField(
        verbose_name="Post (automatic field)",
        max_length=255,
        null=True,
        blank=True,
    )
    users = models.ManyToManyField(AccessPassword, verbose_name='Users Belong This Tag', blank=True, null=True)

    @property
    def total_post(self):
        if self.post:
            return f"{int(self.post):,}"
        return "..."

    @property
    def url(self):
        return f"https://www.instagram.com/explore/tags/" + self.name

    def __str__(self):
        return self.name


def add_map_to_location(sender, instance, **kwargs):
    try:
        if not instance.location_map:
            celery.current_app.send_task("app.tasks.update_location_map", [instance.id])
    except Exception as e:
        print(e)


post_save.connect(add_map_to_location, sender=Location)


def add_post_count_hashtag(sender, instance, **kwargs):
    try:
        if not instance.post:
            celery.current_app.send_task("app.tasks.update_hash_tag")
    except Exception as e:
        print(e)

post_save.connect(add_post_count_hashtag, sender=HashTag)


def update_user_nearby_locations(sender, instance, **kwargs):
    if instance.coordinates:
        if not instance.pk:
            update_coordinates(instance)
        else:
            item = AccessPassword.objects.filter(id=instance.pk)[0]
            if (item.coordinates != instance.coordinates) or (item.coordinate_type != instance.coordinate_type) or not instance.nearby_locations:
                update_coordinates(instance)

            
def update_coordinates(instance):
    coordinates = json.loads(instance.coordinates)
    locations = Location.objects.all()
    if instance.coordinate_type == 'MultiPolygon':
        mp = MultiPolygon([Polygon(pol[0]) for pol in coordinates])
        nearby_locations = [location.id for location in locations if mp.contains(Point(location.lng, location.lat))]
        instance.nearby_locations = json.dumps(nearby_locations)
    elif instance.coordinate_type == 'Polygon':
        poly = Polygon(coordinates[0])
        nearby_locations = [location.id for location in locations if poly.contains(Point(location.lng, location.lat))]
        instance.nearby_locations = json.dumps(nearby_locations)

pre_save.connect(update_user_nearby_locations, sender=AccessPassword)