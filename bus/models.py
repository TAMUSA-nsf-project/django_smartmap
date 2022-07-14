from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Bus(models.Model):
    """
    Active busses.
    """
    latitude = models.FloatField()
    longitude = models.FloatField()
    # driver = models.OneToOneField("BusDriver", on_delete=models.CASCADE)
    driver = models.CharField(max_length=100)
    route = models.CharField(max_length=200)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)  # this field is auto updated anytime the model is updated,

    # therefore it does not need to be updated explicitly

    def __str__(self):
        return f"Bus {self.id}"


class BusStop(models.Model):
    stop_id = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class BusRoute(models.Model):
    # route_id = models.IntegerField()  # don't need, not in json, django auto creates an id field
    name = models.CharField(max_length=200)
    first_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE, related_name="first_stop")
    last_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE, related_name="last_stop")
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BusRouteDetails(models.Model):
    parent_route = models.ForeignKey("BusRoute", on_delete=models.CASCADE)
    bus_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE)
    route_index = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = "Bus Route Details"

    def __str__(self):
        return f"{self.parent_route.name}::{self.bus_stop.name}"


class BusDriver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("access_busdriver_pages", "Can access bus driver pages.")
        ]

    def __str__(self):
        return self.user.username


class TransitLog(models.Model):
    bus_driver = models.ForeignKey("BusDriver", on_delete=models.CASCADE)
    bus_route = models.ForeignKey("BusRoute", on_delete=models.CASCADE)
    last_known_lat = models.FloatField()
    last_known_lng = models.FloatField()
    last_bus_stop = models.CharField(max_length=200)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)  # this field is auto updated anytime the model is updated,

    # therefore it does not need to be updated explicitly

    def __str__(self):
        return f"{self.start_time}::{self.bus_driver.user.username}::{self.bus_route.name}"
