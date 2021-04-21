from django.db import models
from django.db.models.signals import pre_save
from .utils.generate_map import generate_map
# Create your models here.
class AccessPassword(models.Model):
    password = models.CharField(verbose_name='Access Password', max_length=12)


class Location(models.Model):
    name = models.CharField(verbose_name='Location name', max_length=255, null=False, unique=True, blank=False)
    location_id = models.CharField(verbose_name='Location id', max_length=100, null=False, blank=False)
    population = models.CharField(verbose_name='Population', max_length=255, null=False, blank=False)
    location_map = models.CharField(verbose_name='Location map', max_length=300, null=True)

    def __str__(self):
        return self.name


class HashTag(models.Model):
    name = models.CharField(verbose_name='Hash tag name', max_length=255, null=False, unique=True, blank=False)
    post = models.CharField(verbose_name='How many post related this tag', max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name


def add_map_to_location(sender, instance, **kwargs):
    if not instance.location_map and instance.name and instance.location_id:
        instance.location_map = generate_map(location_name=instance.name, location_id=instance.location_id)
        instance.save()


pre_save.connect(add_map_to_location, sender=Location)

    