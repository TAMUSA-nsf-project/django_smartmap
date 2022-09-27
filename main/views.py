from django.shortcuts import render


# Create your views here.

def index(request):
    """Home page."""
    return render(request, 'main/index.html')


def goals_objectives_view(request):
    return render(request, "main/goalsobjectives.html")


def mobile_architecture_view(request):
    return render(request, "main/mobilearchitecture.html")


def security_privacy_view(request):
    return render(request, "main/security_privacy.html")


def arrival_time_accuracy_research_view(request):
    return render(request, "main/arrival_time_accuracy_research.html")


def social_impact_research_view(request):
    return render(request, "main/social_impact.html")


def management_dev_teams_view(request):
    return render(request, "main/management_dev_teams.html")

