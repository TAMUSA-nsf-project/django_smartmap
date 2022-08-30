"""Defines URL patterns for map app."""
from django.urls import path
from . import views

app_name = "map"
urlpatterns = [
    # Map:
    path('map/', views.map_hello_world, name='map'),
    path('routedetails-ajax/', views.getRouteDetailsAJAX, name='routedetails-ajax'),
    path('occupancy-status-ajax/', views.getBusColorDescriptionAJAX, name='occupancy-status-ajax'),

]
