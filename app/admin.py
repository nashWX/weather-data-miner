from django.contrib import admin
from .models import AccessPassword, Location, HashTag

# Register your models here.


class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('location_map',)

admin.site.register(AccessPassword)
admin.site.register(HashTag)
admin.site.register(Location, LocationAdmin)