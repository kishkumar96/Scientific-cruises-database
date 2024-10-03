from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point, MultiLineString, LineString
from django.db import models, transaction  # Added import for transaction
from django_countries.fields import CountryField
from django.utils.html import mark_safe
from uuid import uuid4
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

def handle_antimeridian_crossing(points: List[Tuple[float, float]], tolerance: float = 1e-6) -> MultiLineString:
    if not points:
        return MultiLineString()

    def wrap_longitude(lon):
        if lon > 180:
            return lon - 360
        elif lon < -180:
            return lon + 360
        return lon

    linestrings = []
    current_linestring = [points[0]]

    for i in range(1, len(points)):
        prev_point = points[i - 1]
        current_point = points[i]

        logger.debug(f"Processing segment: {prev_point} to {current_point}")

        if abs(prev_point[0] - current_point[0]) > 180 - tolerance:  # Check for antimeridian crossing
            x1, y1 = prev_point
            x2, y2 = current_point
            x_split = 180 if x1 > 0 else -180  # Determine which side of the antimeridian the split occurs

            # Calculate y (latitude) of the split point using interpolation
            y_split = y1 + (y2 - y1) * (x_split - x1) / (x2 - x1)  

            current_linestring.append((x_split, y_split))  # Add the split point
            linestrings.append(LineString(current_linestring))

            # Start a new linestring segment with the other split point
            current_linestring = [(-x_split, y_split), current_point]  
        else:
            current_linestring.append(current_point)

    linestrings.append(LineString(current_linestring))
    result = MultiLineString(linestrings)
    logger.debug(f"Resulting MultiLineString: {result}")
    return result

def create_multilinestring_route(points: List[Tuple[float, float]]) -> MultiLineString:
    if len(points) < 2:
        return MultiLineString()
    return handle_antimeridian_crossing(points)

class Vessel(models.Model):
    vessel_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vessel_name = models.CharField(max_length=200, verbose_name="Vessel Name")
    vessel_desc = models.TextField(verbose_name="Vessel Description")
    vessel_picture = models.ImageField(upload_to='vessel_images/', verbose_name="Vessel Picture", max_length=10000)
    vessel_credit_url = models.URLField(verbose_name="Vessel Credit URL")

    def image_tag(self):
        if self.vessel_picture:
            return mark_safe(f'<img src="{self.vessel_picture.url}" width="150" />')
        else:
            return "(No Image)"
    image_tag.short_description = 'Image'

    class Meta:
        ordering = ['vessel_name']
        verbose_name = "Vessel"
        verbose_name_plural = "Vessels"

    def __str__(self):
        return self.vessel_name

class CruiseStatus(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']
        verbose_name = "Cruise status"
        verbose_name_plural = "Cruise status"

    def __str__(self):
        return self.name

class Cruise(models.Model):
    cruise_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, verbose_name="Associated Vessel")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Associated User")
    iso2_country = CountryField(blank_label="(select country)")
    cruise_name = models.CharField(max_length=200, verbose_name="Cruise Name")
    cruise_desc = models.TextField(verbose_name="Cruise Description")
    cruise_website_url = models.URLField(verbose_name="Cruise Website URL")
    cruise_doi_url = models.URLField(verbose_name="Cruise DOI URL")
    cruise_ship_name = models.CharField(max_length=100, verbose_name="Cruise Ship Name")
    cruise_ship_flag = models.CharField(max_length=2, verbose_name="Cruise Ship Flag")
    cruise_ship_url = models.URLField(verbose_name="Cruise Ship URL")
    cruise_ship_phone_contact = models.CharField(max_length=50, verbose_name="Cruise Ship Phone Contact")
    cruise_ship_email_contact = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Cruise Ship Email Contact")
    is_multi = models.BooleanField(default=False, verbose_name="Is Multi-Leg")
    img_vessel_path = models.ImageField(upload_to='cruise_images/', blank=True, null=True, verbose_name="Image Vessel Path", max_length=1000)
    status = models.ForeignKey(CruiseStatus, on_delete=models.SET_NULL, null=True, verbose_name="Cruise Status")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Route.objects.filter(cruise=self).exists():
            Route.objects.create(cruise=self)

    class Meta:
        ordering = ['cruise_name']
        verbose_name = "Cruise"
        verbose_name_plural = "Cruises"

    def __str__(self):
        return self.cruise_name

@receiver(post_save, sender=Cruise)
def create_route_for_cruise(sender, instance, created, **kwargs):
    if created and not Route.objects.filter(cruise=instance).exists():
        Route.objects.create(cruise=instance)

class Position(models.Model):
    position_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cruise = models.ForeignKey(Cruise, on_delete=models.CASCADE, related_name='positions')
    date = models.DateField()
    time = models.TimeField()
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    coordinates = gis_models.PointField(geography=True, blank=True, null=True, spatial_index=True)

    def save(self, *args, **kwargs):
        if self.lon is not None and self.lat is not None:
            self.coordinates = Point(float(self.lon), float(self.lat), srid=4326)
        else:
            self.coordinates = None
        super().save(*args, **kwargs)

    @property
    def coordinates_changed(self):
        """Check if coordinates have been modified since the last save."""
        if not self.pk:  # If object is new, coordinates have changed by default
            return True
        original = Position.objects.get(pk=self.pk)
        return original.coordinates != self.coordinates

@receiver(post_save, sender=Position)
def update_route_on_position_save(sender, instance, created, **kwargs):
    cruise = instance.cruise
    if not Route.objects.filter(cruise=cruise).exists():
        Route.objects.create(cruise=cruise)
    cruise.route.update_route()

class Leg(models.Model):
    leg_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cruise = models.ForeignKey(Cruise, on_delete=models.CASCADE, related_name='legs', verbose_name="Associated Cruise")
    leg_number = models.IntegerField(verbose_name="Leg Number")
    departure_port = models.CharField(max_length=50, verbose_name="Departure Port")
    return_port = models.CharField(max_length=50, verbose_name="Return Port")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

    class Meta:
        ordering = ['start_date']
        verbose_name = "Leg"
        verbose_name_plural = "Legs"

    def __str__(self):
        return f"Leg {self.leg_number} of {self.cruise.cruise_name}"

class Route(models.Model):
    cruise = models.OneToOneField(Cruise, on_delete=models.CASCADE, related_name="route")
    path = gis_models.MultiLineStringField(geography=True, blank=True, null=True)

    def update_route(self):
        try:
            positions = self.cruise.positions.order_by('date', 'time')
            points = [(float(pos.lon), float(pos.lat)) for pos in positions if pos.lon is not None and pos.lat is not None]

            if not points:
                logger.warning(f"No valid positions found for cruise {self.cruise}")
                return

            self.path = create_multilinestring_route(points)
            self.save(update_fields=['path'])  # Save only the path field to avoid recursion

            self.segments.all().delete()  # Clear existing segments

            # Create segments
            for i in range(len(points) - 1):
                start_position = positions[i]
                end_position = positions[i + 1]
                segment_path = LineString([points[i], points[i + 1]])
                Segment.objects.create(route=self, path=segment_path, start_position=start_position, end_position=end_position)

        except Exception as e:
            logger.error(f"Error updating route for cruise {self.cruise}: {e}")

    class Meta:
        ordering = ['cruise']
        verbose_name = "Route"
        verbose_name_plural = "Routes"

    def __str__(self):
        return f"Route for {self.cruise.cruise_name}"

@receiver(post_save, sender=Position)
def update_route_on_position_save(sender, instance, created, **kwargs):
    cruise = instance.cruise
    route = cruise.route
    route.update_route()

class Segment(models.Model):
    segment_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='segments')
    path = gis_models.LineStringField(geography=True, blank=True, null=True)
    start_position = models.ForeignKey(Position, related_name='start_segments', on_delete=models.CASCADE)
    end_position = models.ForeignKey(Position, related_name='end_segments', on_delete=models.CASCADE)
    leg = models.ForeignKey(Leg, related_name='segments', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['segment_id']

    def __str__(self):
        return f"Segment from {self.start_position} to {self.end_position}"
    
    def save(self, *args, **kwargs):
        if self.start_position.coordinates and self.end_position.coordinates:
            self.path = LineString([self.start_position.coordinates, self.end_position.coordinates])
        super().save(*args, **kwargs)

class Scientist(models.Model):
    scientist_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cruise = models.ForeignKey(Cruise, on_delete=models.CASCADE, related_name='scientists', verbose_name="Associated Cruise")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    is_chief_scientist = models.BooleanField(default=False, verbose_name="Is Chief Scientist")
    email_contact = models.EmailField(max_length=200, verbose_name="Email Contact")
    phone_contact = models.CharField(max_length=50, blank=True, null=True, verbose_name="Phone Contact")

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Scientist"
        verbose_name_plural = "Scientists"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class RefList(models.Model):
    list_id = models.AutoField(primary_key=True)
    list_type = models.CharField(max_length=10, verbose_name="List Type")
    list_desc = models.CharField(max_length=50, verbose_name="List Description")

    class Meta:
        ordering = ['list_type']
        verbose_name = "Reference List"
        verbose_name_plural = "Reference Lists"

    def __str__(self):
        return f"{self.list_type} - {self.list_desc}"
