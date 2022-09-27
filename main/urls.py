"""Defines URL patterns for main."""
from django.urls import path
from . import views

app_name = "main"
urlpatterns = [
    # Home page
    path('', views.index, name='index'),

    path('goals/', views.goals_objectives_view, name='goals-objectives'),
    path('mobile-architecture/', views.mobile_architecture_view, name='mobile-architecture'),
    path('security-privacy/', views.security_privacy_view, name='security-privacy'),
    path('arrival-time-accuracy-research/', views.arrival_time_accuracy_research_view, name='arrival-time-accuracy-research'),
    path('social-impact-research/', views.social_impact_research_view, name='social-impact-research'),
    path('management-dev-teams/', views.management_dev_teams_view, name='management-dev-teams'),

]
