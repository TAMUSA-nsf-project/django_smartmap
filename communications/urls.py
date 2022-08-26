"""Defines URL patterns for map app."""
from django.urls import path
from . import views

app_name = "communications"
urlpatterns = [
    # Announcements:
    path('announcements/', views.announcements_view, name='announcements'),

]
