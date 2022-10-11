import csv
from typing import List, Tuple
import json
import re
import itertools


# if today == 6:  # Sunday
#     return "F"
# elif today == 5:  # Saturday
#     return "S"
# else:  # Weekday
#     return "W"


# "Stop Name": "Martin & Navarro",
# "bus_stop": 71839,
# "bus_route": "Route 51 (reverse)",
# "day_of_week": "W",
# "scheduled_time": "9:50"


class BusStop:
    counter = 0

    def __init__(self, name: str, coords: Tuple[float, float], number=None):
        self.name = name
        self.latitude, self.longitude = coords

        if number:
            self.number = number
        else:
            # otherwise use the class counter
            self.number = BusStop.counter
            BusStop.counter += 1

    def __str__(self):
        return self.name

    def __int__(self):
        return self.number

    def __repr__(self):
        return self.name


class RouteSchedule:
    def __init__(self, route_name: str, day_of_week: str, reverse=False):
        self.route_name = route_name  # + " (reverse)" if reverse else route_name
        self.day_of_week = day_of_week
        self.reverse = reverse
        self.file_prefix = route_name + "_" + day_of_week
        self.bus_stop_schedules = []
        self.bus_stop_names = []

    def __repr__(self):
        return f"{self.route_name}, {self.day_of_week}"

    @staticmethod
    def _check_time_format(time) -> bool:
        """
        Checks if the provided time is in correct format. Provided time can be an int or string like "12:30".
        """
        return bool(re.fullmatch(r"^\d{2}:?\d{2}$", time))

    def _convert_time(self, time):

        # force convert time to string and zero pad (4 zeros)
        x = str(time).zfill(4)

        # check for bad time format provided by user
        if not RouteSchedule._check_time_format(x):
            raise ValueError(f"Invalid time format: '{self}' -> '{time}'")

        # insert a colon separator if needed
        if ":" not in x:
            x = re.sub(r'(\d\d)(\d\d)', r'\1:\2', x)
        return x

    def addSchedule(self, bus_stop: BusStop, scheduled_times: List):
        if bus_stop.name not in self.bus_stop_names:
            self.bus_stop_names.append(bus_stop.name)

        self.bus_stop_schedules.append((bus_stop, scheduled_times))

    def getRouteSchedule(self):
        res = []
        bus_stop_schedules = self.bus_stop_schedules  # .reverse() if self.reverse else self.bus_stop_schedules

        if not bus_stop_schedules:
            print("No schedules have been added. Add a schedule with method 'addSchedule'.")

        for bus_stop, times in bus_stop_schedules:
            for time in times:
                res.append({"Stop Name": str(bus_stop),
                            "bus_stop": int(bus_stop),
                            "bus_route": self.route_name,
                            "day_of_week": self.day_of_week,
                            "scheduled_time": self._convert_time(time),
                            })
        return {self.route_name: res}

    def exportDataToCSV(self):
        zipped_times = itertools.zip_longest(*[times for _, times in self.bus_stop_schedules], fillvalue="")
        field_names = self.bus_stop_names + ["route_name", "day_of_week"]
        with open(self.file_prefix + ".csv", 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            for item in zipped_times:
                x = list(item) + [self.route_name, self.day_of_week]
                _dict = dict(zip(field_names, x))
                writer.writerow(_dict)

    def exportRouteScheduleToJSON(self):
        with open(self.file_prefix + ".json", "w", encoding='utf-8') as f:
            json.dump(self.getRouteSchedule(), f, ensure_ascii=False, indent=4)
        print("Done")

    def getRouteBusStops(self):
        """todo"""
        pass

    def exportRouteBusStopCoordsToJSON(self):
        """todo"""
        pass



