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
