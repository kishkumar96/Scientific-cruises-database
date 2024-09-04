from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.
# my_app/views.py

# cruises/views.py
# cruises/views.py
from rest_framework import viewsets
from .models import Cruise, CruiseStatus
from .serializers import CruiseSerializer
from django.http import HttpResponse
from django.conf import settings
import os 
from .serializers import CruiseSerializer, ScientistSerializer, CruiseStatusSerializer

from .models import Scientist
from .serializers import ScientistSerializer


class CruiseStatusViewSet(viewsets.ModelViewSet):
    queryset = CruiseStatus.objects.all()
    serializer_class = CruiseStatusSerializer


class ScientistViewSet(viewsets.ModelViewSet):
    queryset = Scientist.objects.all()
    serializer_class = ScientistSerializer
class CruiseViewSet(viewsets.ModelViewSet):
    queryset = Cruise.objects.prefetch_related('legs', 'positions', 'scientists').all()  # This prefetches the related Legs
    serializer_class = CruiseSerializer

    def get_serializer_context(self):
        # Adds the request to the serializer context
        context = super(CruiseViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


@ensure_csrf_cookie
def index(request):
    try:
        with open(os.path.join(settings.BASE_DIR, 'my-cruise-app/build', 'index.html')) as file:
            return HttpResponse(file.read())
    except FileNotFoundError:
        return HttpResponse(
            "Build your React app and ensure the path is correct.", status=501
        )
