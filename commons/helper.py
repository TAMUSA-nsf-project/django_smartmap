from django.db.models import F
from bus.models import BusRoute, BusRouteDetails, BusStop


def getAllActiveRoutesDropDown():
    """
        Method to return all the active bus routes from the database.
        The returned data will be in the format.
        { primary_key : <route_name>  <first_stop> --> <last_stop>}
    """
    allRoutes = {}
    for route in BusRoute.objects.filter(active=True).all():
        allRoutes[route.pk] = f"{route.getDisplayName()}  {route.first_stop} → {route.last_stop}"
    return allRoutes


def getRoutesDetails(route_id):
    """
        Method to return all the stops in a given route.
    """
    allStops = BusRouteDetails.objects.filter(
        parent_route=route_id).order_by('route_index').values(
        BusRouteName=F('parent_route__name'),
        BusStopIndex=F('route_index'),
        BusRouteId=F('parent_route'),
        BusStopName=F('bus_stop__name'),
        BusStopLatitude=F('bus_stop__latitude'),
        BusStopLongitude=F('bus_stop__longitude'),
        BusStopNumber = F('bus_stop__stop_id'),
        LocationPinColor = F('parent_route__color_code')
    )
    return allStops
