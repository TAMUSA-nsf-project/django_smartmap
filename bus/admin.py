from django.contrib import admin

# Register your models here.
from .models import BusStop, BusRoute, BusRouteDetails, BusSchedule
from .models import BusDriver
from .models import Bus
from .models import TransitLog
from .models import TransitLogEntry

admin.site.register(BusStop)
admin.site.register(BusRoute)
admin.site.register(BusRouteDetails)
admin.site.register(BusDriver)
admin.site.register(Bus)
admin.site.register(TransitLog)
admin.site.register(TransitLogEntry)
admin.site.register(BusSchedule)
