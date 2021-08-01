import pytz

from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from decouple import config
import celery
# Create your models here.


class AccessPassword(models.Model):
    password = models.CharField(verbose_name="Access Password", max_length=12)

    def __str__(self) -> str:
        return "Access password for UI"


class Location(models.Model):
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
    lat = models.CharField(
        verbose_name="Latitude", null=True, max_length=50, blank=True
    )
    lng = models.CharField(
        verbose_name="Longitude", null=True, max_length=50, blank=True
    )
    can_retrive_population = models.BooleanField(verbose_name='can retrive population', default=True)

    def __str__(self):
        return self.name
    
    @property
    def insta_url(self):
        return f"https://www.instagram.com/explore/locations/{self.location_id}"


class Warning(models.Model):
    timezone = config('timezone', default='America/New_York', cast=str)
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
            return local_dt.strftime("%I:%M")
        return None

    @property
    def end(self):
        if self.end_time:
            local_dt = timezone.localtime(self.end_time, pytz.timezone(self.timezone))
            return local_dt.strftime("%I:%M")
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
        return start.strftime('%Y-%m-%d %I:%M')

    @property
    def local_end(self):
        end = timezone.localtime(self.end_time, pytz.timezone(self.timezone))
        return end.strftime('%Y-%m-%d %I:%M')
    

    @staticmethod
    def get_recent_warnings(_type='TORNADO'):
        latest_warnings = Warning.objects.filter(warning_type=_type).order_by('-start_time')
        warnings = []
        count = 0
        for latest_warning in latest_warnings:
            if all([latest_warning.start_time != warning.start_time and latest_warning.end_time > warning.start_time for warning in warnings]):
                warnings.append(latest_warning)
                count +=1
            if count >= 10:
                break
        
        warning_suggestions = []
        for i in range(0, len(warnings)):
            if len(warnings) > 1 and i < len(warnings)/2:
                warning_suggestions.append({
                    'start': warnings[i],
                    'end': warnings[len(warnings)-(i+1)]
                })
            if len(warnings) == 1:
                 warning_suggestions.append({
                    'start': warnings[0],
                    'end': warnings[0]
                })

        return warning_suggestions


        


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


    @property
    def url(self):
        return f'https://www.instagram.com/explore/tags/'+self.name

    def __str__(self):
        return self.name


def add_map_to_location(sender, instance, **kwargs):
    try:
        if not instance.location_map:
            celery.current_app.send_task('app.tasks.update_location_map', [instance.id])
    except Exception as e:
        print(e)
post_save.connect(add_map_to_location, sender=Location)


def add_post_count_hashtag(sender, instance, **kwargs):
    try:
        if not instance.post:
            celery.current_app.send_task('app.tasks.update_hash_tag', [instance.name])
    except Exception as e:
        print(e)
post_save.connect(add_post_count_hashtag, sender=HashTag)
