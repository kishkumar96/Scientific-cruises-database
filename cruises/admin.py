from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from .models import Vessel, Cruise, Leg, Scientist, Position, RefList, CruiseStatus, Route, Segment
from .resources import VesselResource, CruiseStatusResource, CruiseResource, PositionResource, LegResource, ScientistResource

class LegInline(admin.TabularInline):
    model = Leg
    extra = 0
    fields = ['leg_number', 'departure_port', 'return_port', 'start_date', 'end_date']
    ordering = ['leg_number']

class ScientistInline(admin.TabularInline):
    model = Scientist
    extra = 0
    fields = ['first_name', 'last_name', 'is_chief_scientist', 'email_contact', 'phone_contact']
    ordering = ['last_name', 'first_name']

class PositionInline(admin.TabularInline):
    model = Position
    extra = 0
    fields = ['date', 'time', 'lat', 'lon']
    ordering = ['-date', '-time']

class SegmentInline(admin.TabularInline):
    model = Segment
    extra = 0
    fields = ['start_position', 'end_position', 'leg', 'path']
    readonly_fields = ['path']
    ordering = ['start_position']

class RouteInline(admin.StackedInline):
    model = Route
    can_delete = False
    verbose_name_plural = 'Route'
    fk_name = 'cruise'

@admin.register(Vessel)
class VesselAdmin(GISModelAdmin, ImportExportModelAdmin):
    list_display = ['vessel_name', 'vessel_desc', 'vessel_picture', 'image_tag']
    search_fields = ['vessel_name']
    resource_class = VesselResource

    def image_tag(self, obj):
        if obj.vessel_picture:
            return format_html('<img src="{}" style="width: 150px; height:auto;">', obj.vessel_picture.url)
        return "No Image"
    image_tag.short_description = 'Image'

@admin.register(Cruise)
class CruiseAdmin(GISModelAdmin, ImportExportModelAdmin):
    list_display = ['cruise_name', 'vessel', 'user', 'iso2_country', 'status']
    search_fields = ['cruise_name', 'vessel__vessel_name', 'user__username']
    list_filter = ['iso2_country', 'status']
    ordering = ['cruise_name']
    inlines = [LegInline, ScientistInline, PositionInline, RouteInline]
    resource_class = CruiseResource

@admin.register(Leg)
class LegAdmin(ImportExportModelAdmin):
    list_display = ['leg_number', 'cruise', 'departure_port', 'return_port', 'start_date', 'end_date']
    search_fields = ['cruise__cruise_name', 'departure_port', 'return_port']
    list_filter = ['departure_port', 'return_port']
    ordering = ['cruise', 'leg_number']
    resource_class = LegResource

@admin.register(Scientist)
class ScientistAdmin(ImportExportModelAdmin):
    list_display = ['first_name', 'last_name', 'cruise', 'is_chief_scientist', 'email_contact', 'phone_contact']
    search_fields = ['first_name', 'last_name', 'cruise__cruise_name']
    list_filter = ['is_chief_scientist']
    ordering = ['last_name', 'first_name']
    resource_class = ScientistResource

@admin.register(Position)
class PositionAdmin(GISModelAdmin, ImportExportModelAdmin):
    list_display = ('date', 'time', 'lat', 'lon', 'coordinates')
    search_fields = ['cruise__cruise_name']
    ordering = ['-date', '-time']
    resource_class = PositionResource

@admin.register(RefList)
class RefListAdmin(ImportExportModelAdmin):
    list_display = ['list_type', 'list_desc']
    search_fields = ['list_type', 'list_desc']
    ordering = ['list_type']

@admin.register(CruiseStatus)
class CruiseStatusAdmin(ImportExportModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    resource_class = CruiseStatusResource

@admin.register(Route)
class RouteAdmin(GISModelAdmin, ImportExportModelAdmin):
    list_display = ['cruise', 'path']
    search_fields = ['cruise__cruise_name']
    ordering = ['cruise']
    inlines = [SegmentInline]

@admin.register(Segment)
class SegmentAdmin(GISModelAdmin, ImportExportModelAdmin):
    list_display = ['start_position', 'end_position', 'leg', 'path']
    search_fields = ['start_position__date', 'end_position__date', 'leg__cruise__cruise_name']
    ordering = ['start_position__date', 'end_position__date']

# Register other models as before...
