"""Defines URL patterns for map app."""
from django.urls import path
from . import views

app_name = "bus"
urlpatterns = [
    # Bus driver
    path('busdriver/', views.busdriver_view, name='busdriver-page'),

    # Simulation file
    path('simulation/', views.simulation_view, name='simulation-page'),
    path('simulation-ajax/', views.simulation_ajax, name='simulation-ajax'),

]