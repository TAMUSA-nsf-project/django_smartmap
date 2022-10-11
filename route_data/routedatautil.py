import csv
import json
import re
from enum import Enum

ROUTE_DATA_FILE = 'route-data.csv'
ROUTE_SCHEDULE_FILE = 'route-schedule.csv'


class InputDataType(Enum):
    ROUTE = 1
    SCHEDULE = 2


def GenerateJsonFile(file_type: InputDataType):
    manager = RouteManager(file_type)
    filename = ''
    if file_type == InputDataType.ROUTE:
        filename = ROUTE_DATA_FILE
    elif file_type == InputDataType.SCHEDULE:
        filename = ROUTE_SCHEDULE_FILE
    with open(filename, "r", encoding='utf-8-sig') as file:
        fileContents = csv.DictReader(file)
        for item in fileContents:
            r_name = item['bus_route']
            manager.AddRouteIfNotExist(r_name)
            manager.ProcessData(r_name, item)
        if file_type == InputDataType.ROUTE:
            manager.exportRouteToJSON()
        elif file_type == InputDataType.SCHEDULE:
            manager.exportRouteScheduleToJSON()


class BusStop:

    # Stop Name and Stop Number/ID are mandatory
    def __init__(self, name: str, stop_id):
        self.stopName = name
        self.latitude = None
        self.longitude = None
        self.stopNumber = stop_id
        self.route = None
        self.orderOnRoute = None
        self.schedule = None

    def __str__(self):
        return self.stopName

    def __int__(self):
        return self.stopNumber

    def __repr__(self):
        return self.stopName


class RouteManager:

    def __init__(self, d_type: InputDataType):
        self.type = d_type
        self.busSchedules = {}
        self.busRoutes = {}

    def AddBusStopsForRoute(self, data):
        route = data['bus_route']
        self.busRoutes[route].append(
            {"Stop Name": data['Stop Name'],
             "Stop Number": data['Stop Number'],
             "Lat": float(data['Lat']),
             "Lng": float(data['Lng']),
             "route": route,
             "Order on Route": data['Order on Route']}
        )

    def AddScheduleForBusStops(self, data):
        route = data['bus_route']
        day_of_week = data['day_of_week']
        del data['bus_route']
        del data['day_of_week']
        for key in data.keys():
            val = data[key]
            if val:
                stopName, stopNumber = key.split('#')
                # Todo: fix later
                # stopName = stopName.strip('ï»¿')
                self.busSchedules[route].append(
                    {"Stop Name": stopName,
                     "bus_stop": int(stopNumber),
                     "bus_route": route,
                     "day_of_week": day_of_week,
                     "scheduled_time": self._convert_time(val),
                     }
                )

    def AddRouteIfNotExist(self, route_name):
        if self.type == InputDataType.ROUTE:
            if route_name not in self.busRoutes:
                self.busRoutes[route_name] = []
        elif self.type == InputDataType.SCHEDULE:
            if route_name not in self.busSchedules:
                self.busSchedules[route_name] = []

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
        if not RouteManager._check_time_format(x):
            raise ValueError(f"Invalid time format: '{self}' -> '{time}'")

        # insert a colon separator if needed
        if ":" not in x:
            x = re.sub(r'(\d\d)(\d\d)', r'\1:\2', x)
        return x

    def ProcessData(self, route_name, data_row):
        if self.type == InputDataType.ROUTE:
            if route_name in self.busRoutes:
                self.AddBusStopsForRoute(data_row)
        elif self.type == InputDataType.SCHEDULE:
            if route_name in self.busSchedules:
                self.AddScheduleForBusStops(data_row)

    # def getRouteSchedule(self):
    #     res = []
    #     bus_stop_schedules = self.bus_stop_schedules
    #
    #     if not bus_stop_schedules:
    #         print("No schedules have been added. Add a schedule with method 'addSchedule'.")
    #
    #     for bus_stop, times in bus_stop_schedules:
    #         for time in times:
    #             res.append({"Stop Name": str(bus_stop),
    #                         "bus_stop": int(bus_stop),
    #                         "bus_route": self.route_name,
    #                         "day_of_week": self.day_of_week,
    #                         "scheduled_time": self._convert_time(time),
    #                         })
    #     return {self.route_name: res}

    def exportRouteScheduleToJSON(self):
        with open("testSchedule" + ".json", "w", encoding='utf-8') as f:
            json.dump(self.busSchedules, f, ensure_ascii=False, indent=4)
        print("Done")

    def exportRouteToJSON(self):
        with open("testR" + ".json", "w", encoding='utf-8') as f:
            json.dump(self.busRoutes, f, ensure_ascii=False, indent=4)
        print("Done")

    def getRouteBusStops(self):
        """todo"""
        pass

    def exportRouteBusStopCoordsToJSON(self):
        """todo"""
        pass


GenerateJsonFile(InputDataType.SCHEDULE)
GenerateJsonFile(InputDataType.ROUTE)
