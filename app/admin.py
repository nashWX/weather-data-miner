from django.contrib import admin
from .models import AccessPassword, Location, HashTag, Warning

# Register your models here.


class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('location_map',)
    search_fields = ['name', 'city_name']

class WarningAdmin(admin.ModelAdmin):
    list_filter = ("start_time", "end_time", 'warning_type')
    ordering = ('-start_time', '-end_time')

admin.site.register(AccessPassword)
admin.site.register(HashTag)
admin.site.register(Location, LocationAdmin)
admin.site.register(Warning, WarningAdmin)