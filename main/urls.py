"""Defines URL patterns for main."""
from django.urls import path
from . import views

app_name = "main"
urlpatterns = [
    # Home page
    path('', views.index, name='index'),


    path('goals/', views.goals_objectives_view, name='goals-objectives'),
]