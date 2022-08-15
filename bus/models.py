from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import googlemaps
from googlemaps.directions import directions

DEFAULT_COLOR_CODE = "#FF0000"

gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)


# Create your models here.
class Bus(models.Model):
    """
    Active busses.
    """
    latitude = models.FloatField()
    longitude = models.FloatField()
    # driver = models.OneToOneField("BusDriver", on_delete=models.CASCADE)
    driver = models.CharField(max_length=100)
    route = models.ForeignKey("BusRoute", on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField(default=None, blank=True, null=True)
    end_time = models.DateTimeField(default=None, blank=True, null=True)
    transit_log_id = models.PositiveIntegerField(default=None)
    seat_availability = models.CharField(default="green", max_length=50)  # todo only values "green", "red", "yellow"

    def getBusColorStaticUrl(self) -> str:
        """
        Returns URL to appropriate static colored bus icon based on seat availability.

        'green' = many open seats
        'yellow' = <3 open seats
        'red' = no open seats
        """
        # TODO hardcoded hack for google cloud deployment, change STATIC_URL value in settings
        return "https://storage.googleapis.com/nsf-2131193-18902-static-files/" + "map/icons/" + self.seat_availability + "_bus.png"

    def getLatLngTuple(self):
        return self.latitude, self.longitude

    def getCoordinates(self):
        return self.getLatLngTuple()

    class Meta:
        verbose_name_plural = 'buses'  # django automatically capitalizes this in the admin site

    def __str__(self):
        return f"Bus {self.id}"


class BusStop(models.Model):
    stop_id = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def getLatLngTuple(self):
        return self.latitude, self.longitude

    def getCoordinates(self):
        return self.getLatLngTuple()

    def __str__(self):
        return self.name


class BusRoute(models.Model):
    # route_id = models.IntegerField()  # don't need, not in json, django auto creates an id field
    name = models.CharField(max_length=200)
    first_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE, related_name="first_stop")
    last_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE, related_name="last_stop")
    active = models.BooleanField(default=False)
    color_code = models.CharField(max_length=10, default=DEFAULT_COLOR_CODE)
    gmaps_polyline_encoding = models.TextField(default="")
    gmaps_polyline_bounds = models.CharField(default="", max_length=200)

    def getGmapsDirectionsServiceResult(self):
        """
        Returns an object representing a Google Map's DirectionsService API result.
        """
        origin_coords = self.first_stop.getCoordinates()
        dest_coords = self.last_stop.getCoordinates()
        res = directions(gmaps, origin=origin_coords, destination=dest_coords, mode="transit", transit_mode="bus")

        class GmapsDirectionsServiceResult:
            def __init__(self):
                self._res = res

            def getGmapsPolylineEncoding(self) -> str:
                """
                Returns the ascii string encoding of the polyline calculated by Google's Directions Service API.
                """
                polyline_encoding = self._res[0]['overview_polyline']['points']
                if not polyline_encoding:
                    raise ValueError("BusRoute Gmaps polyline encoding is empty.")
                return polyline_encoding

            def getGmapsPolylineBounds(self) -> dict:
                """
                Returns the bounds of the polyline as determined by Google's Directions Service API.
                Example: {'northeast': {'lat': 29.422504, 'lng': -98.4895075}, 'southwest': {'lat': 29.3468565, 'lng': -98.5465827}}
                """
                return self._res[0]['bounds']

            def __repr__(self):
                return str(self._res)

        return GmapsDirectionsServiceResult()

    def __str__(self):
        return self.name


class BusRouteDetails(models.Model):
    parent_route = models.ForeignKey("BusRoute", on_delete=models.CASCADE)
    bus_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE)
    route_index = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'bus route details'

    def __str__(self):
        return f"{self.parent_route.name}: {self.bus_stop.name}"


class BusDriver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("access_busdriver_pages", "Can access bus driver pages.")
        ]

    def __str__(self):
        return self.user.username


class TransitLog(models.Model):
    # bus_driver = models.ForeignKey("BusDriver", on_delete=models.DO_NOTHING)
    driver = models.CharField(max_length=100)
    bus_route = models.ForeignKey("BusRoute", on_delete=models.DO_NOTHING)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus_route.name}, {self.driver}, {self.date_added.strftime('%Y-%m-%d %H:%M:%S')}"


class TransitLogEntry(models.Model):
    transit_log = models.ForeignKey("TransitLog", on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.time_stamp}, Lat: {self.latitude}, Lng: {self.longitude}"
