from django.shortcuts import render

# Create your views here.

from .models import Announcement


def announcements_view(request):
    announcements = Announcement.objects.order_by('-date_added')
    context = {
        'announcements': announcements,
    }
    return render(request, 'communications/announcements.html', context)
