from django.contrib import admin

# Register your models here.
from .models import BusStop, BusRoute, BusRouteStop

admin.site.register(BusStop)
admin.site.register(BusRoute)
admin.site.register(BusRouteStop)