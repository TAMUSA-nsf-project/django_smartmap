from django.shortcuts import render

# Create your views here.

def index(request):
    """Home page."""
    return render(request, 'main/index.html')