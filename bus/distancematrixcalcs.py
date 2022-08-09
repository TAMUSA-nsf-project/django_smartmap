import googlemaps
from datetime import datetime
from googlemaps.distance_matrix import distance_matrix
from django.conf import settings
import time

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed


def timeit(func):
    """Decorator function used to time the execution of functions."""

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ret = func(*args, **kwargs)
        finish = time.perf_counter()
        runtime = round(finish - start)
        print(f"{func.__name__} took {runtime} second(s)")
        return ret

    return wrapper


gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)


def calc_duration(origin, dest, timenow):
    """
    Calculates transit duration between origin and dest. Meant for only one origin, one dest.
    """
    res = distance_matrix(gmaps, origins=origin, destinations=dest,
                          transit_mode="bus",
                          departure_time=timenow)
    return res['rows'][0]['elements'][0]['duration']


# @timeit
def calc_est_arrival_times(socket_data, json_data):
    """
    This method calculates the estimated arrival time from a bus's current position to every bus stop on its route.
    Bypasses Distance Matrix API usage limit of 25 destinations by using multithreading.
    """
    # data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }

    bus_route = socket_data["selected_route"]
    origin = (socket_data['bus_lat'], socket_data['bus_lng'])
    stop_data = json_data[bus_route]

    # must preserve original array's indices for parallel computing because threads/processes can finish out of order
    stops_latlng = {index: (stop["Lat"], stop["Lng"]) for index, stop in enumerate(stop_data)}

    # current time
    timenow = datetime.now()

    # Note: I observed multithreading to be about 2x as fast as multiprocessing in this case
    with ThreadPoolExecutor() as executor:
        # submit calc_duration to the thread pool
        futures = {index: executor.submit(calc_duration, origin, stop, timenow) for index, stop in stops_latlng.items()}

        # wait for the threads to complete
        for _ in as_completed(futures.values()):
            pass

        # get the results out of the futures
        res = [futures[key].result() for key in sorted(futures.keys())]

    # update stop_data dict
    for i in range(len(stop_data)):
        stop_data[i]['est_arrival'] = res[i]['text']

    # return the updated dict as value of new dict with the route as the key
    return {bus_route: stop_data}


def main():
    pass


# The following prevents RuntimeError for 'spawn' and 'forkserver' start_methods:
if __name__ == "__main__":
    main()
