import googlemaps
from datetime import datetime
from googlemaps.distance_matrix import distance_matrix
from django.conf import settings


# updates json_data dict as well
def calc_est_arrival_times(socket_data, json_data):
    """
    This contains a way of bypassing the Distance Matrix API usage limit of 25 destinations by passing only
    one destination at a time. It's very slow without parallel computing.
    """
    # data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }

    bus_route = socket_data["selected_route"]
    stop_data = json_data[bus_route]
    stops_latlng = [(stop["Lat"], stop["Lng"]) for stop in stop_data]

    timenow = datetime.now()

    gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)
    res = [distance_matrix(gmaps, origins=(socket_data['bus_lat'], socket_data['bus_lng']), destinations=stop, transit_mode="bus",
                          departure_time=timenow) for stop in stops_latlng]

    for i in range(len(stop_data)):
        stop_data[i]['est_arrival'] = res[i]['rows'][0]['elements'][0]['duration']['text']

    return {bus_route: stop_data}









def main():
    pass


if __name__ == "__main__":
    main()