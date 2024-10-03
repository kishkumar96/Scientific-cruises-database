from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Cruise, Leg, Scientist, Vessel, CruiseStatus, Position, Route

class VesselSerializer(serializers.ModelSerializer):
    vessel_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Vessel
        fields = ('vessel_id', 'vessel_name', 'vessel_desc', 'vessel_picture_url', 'vessel_credit_url')

    def get_vessel_picture_url(self, obj):
        request = self.context.get('request')
        if obj.vessel_picture and request:
            return request.build_absolute_uri(obj.vessel_picture.url)
        return None

class LegSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leg
        fields = ['leg_number', 'departure_port', 'return_port', 'start_date', 'end_date']

class ScientistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scientist
        fields = ['first_name', 'last_name']

class PositionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Position
        geo_field = "coordinates"
        fields = ('position_id', 'date', 'time', 'lat', 'lon', 'coordinates')

class RouteSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Route
        geo_field = "path"
        fields = ('path',)

class CruiseSerializer(serializers.ModelSerializer):
    legs = LegSerializer(many=True, read_only=True)
    scientists = ScientistSerializer(many=True, read_only=True)
    positions = PositionSerializer(many=True, read_only=True)
    route = RouteSerializer(read_only=True)
    status_name = serializers.SerializerMethodField()
    vessel_details = VesselSerializer(source='vessel', read_only=True)

    class Meta:
        model = Cruise
        fields = [
            'cruise_id', 'iso2_country', 'cruise_name', 'legs', 'scientists',
            'status_name', 'vessel_details', 'positions', 'route'
        ]

    def get_status_name(self, obj):
        return obj.status.name if obj.status else None

class CruiseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CruiseStatus
        fields = ['id', 'name']
