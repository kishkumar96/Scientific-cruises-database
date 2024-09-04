from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CruiseViewSet, ScientistViewSet, CruiseStatusViewSet

router = DefaultRouter()
router.register(r'cruises', CruiseViewSet)
router.register(r'scientists', ScientistViewSet)
router.register(r'statuses', CruiseStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
