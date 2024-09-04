from import_export import resources
from .models import Vessel, CruiseStatus, Cruise, Position, Leg, Scientist

class VesselResource(resources.ModelResource):
    class Meta:
        model = Vessel

class CruiseStatusResource(resources.ModelResource):
    class Meta:
        model = CruiseStatus

class CruiseResource(resources.ModelResource):
    class Meta:
        model = Cruise

class PositionResource(resources.ModelResource):
    class Meta:
        model = Position
        import_id_fields = ['position_id']
        fields = ('position_id', 'cruise', 'date', 'time', 'lat', 'lon', 'coordinates')

class LegResource(resources.ModelResource):
    class Meta:
        model = Leg

class ScientistResource(resources.ModelResource):
    class Meta:
        model = Scientist
