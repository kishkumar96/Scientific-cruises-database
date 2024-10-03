from django import forms
from django.contrib.gis import forms as gis_forms
from django.contrib.gis.geos import Point
from .models import Position

class PositionForm(gis_forms.ModelForm):
    latitude = forms.FloatField(required=False, help_text="Enter latitude")
    longitude = forms.FloatField(required=False, help_text="Enter longitude")

    class Meta:
        model = Position
        fields = '__all__'
        widgets = {
            'coordinates': gis_forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500})
        }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        if latitude is not None and longitude is not None:
            cleaned_data['coordinates'] = Point(longitude, latitude)
        return cleaned_data

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
