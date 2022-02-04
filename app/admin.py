from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import AccessPassword, Location, HashTag, Util, Warning

# Register your models here.


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'lng', 'population')
    readonly_fields = ('location_map',)
    search_fields = ['name', 'city_name']
    list_filter = ('city_name', 'state_name')

class AccessPasswordAdmin(admin.ModelAdmin):
    readonly_fields = ('nearby_locations',)
class WarningAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = ['location__state_name', 'location__city_name']
    list_display = ('location', 'warning_type', '_start_time', '_end_time')
    list_filter = ("start_time", "end_time", 'warning_type', 'location__state_name', 'location__city_name')
    ordering = ('-start_time', '-end_time')

    def _start_time(self, obj):
        return mark_safe(obj.start)

    def _end_time(self, obj):
        return mark_safe(obj.end)
    
    class Media:
        css = {
            'all': ('css/admin.css',),
        }

class UtilAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not Util.objects.exists()
    
admin.site.register(AccessPassword, AccessPasswordAdmin)
admin.site.register(HashTag)
admin.site.register(Util, UtilAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Warning, WarningAdmin)