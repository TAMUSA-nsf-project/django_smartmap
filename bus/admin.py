from django.contrib import admin

# Register your models here.
from .models import BusStop, BusRoute, BusRouteDetails
from .models import BusDriver
from .models import Bus

admin.site.register(BusStop)
admin.site.register(BusRoute)
admin.site.register(BusRouteDetails)
admin.site.register(BusDriver)
admin.site.register(Bus)
