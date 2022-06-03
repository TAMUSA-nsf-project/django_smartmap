import googlemaps
from datetime import datetime
from googlemaps.distance_matrix import distance_matrix


from django.conf import settings

# updates json_data dict as well
def calc_est_arrival_times(socket_data, json_data):
    """
    TODO Figure out way around Distance Matrix API usage limit: Maximum of 25 origins or 25 destinations per request
    Routes such as 'Route 51' have more than 25 stops and will cause error: "googlemaps.exceptions.ApiError: MAX_DIMENSIONS_EXCEEDED"
    """
    # data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }

    bus_route = socket_data["selected_route"]
    stop_data = json_data[bus_route]
    stops_latlng = [(stop["Lat"], stop["Lng"]) for stop in stop_data]

    gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)
    res = distance_matrix(gmaps, origins=(socket_data['bus_lat'], socket_data['bus_lng']), destinations=stops_latlng, transit_mode="bus",
                          departure_time=datetime.now())

    for i in range(len(stop_data)):
        stop_data[i]['est_arrival'] = res['rows'][0]['elements'][i]['duration']['text']

    return {bus_route: stop_data}