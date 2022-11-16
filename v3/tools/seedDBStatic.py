# First argument is the name of the geojson file to upload
# Second argument is a if the file contains zones that are always active
# 
# python3 seedDBStatic.py file a --> zones always active
# python3 seedDBStatic.py fil --> zones not always active

import pymongo
import sys
import json
import numpy
import math
import matplotlib.path as mplPath
from datetime import datetime
from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


class Water(EnumMeta):
    DOCK = "dock"
    RESERVOIR = "reservoir"
    RIVERBANK = "riverbank"
    WATER = "water"
    WETLAND = "wetland"


class School(EnumMeta):
    COLLEGE = "college"
    SCHOOL = "school"
    UNIVERSITY = "university"


class Government(EnumMeta):
    FIRE_STATION = "fire_station"
    POLICE = "police"
    COURTHOUSE = "courthouse"
    WATER_WORKS = "water_works"
    WASTEWATER_PLANT = "wastewater_plant"
    PRISON = "prison"
    PUBLIC_BUILDING = "public_building"
    LIBRARY = "library"
    POST_OFFICE = "post_office"


class Hospital(EnumMeta):
    VETERINARY = "veterinary"
    HOSPITAL = "hospital"
    OPTICIAN = "optician"
    DENTIST = "dentist"
    DOCTORS = "doctors"
    CLINIC = "clinic"

class Building(EnumMeta):
    BUILDING = "building"


class Misc(EnumMeta):
    TRACK = "track"


CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"
ANGLES = [2*math.pi / 3, math.pi, 4*math.pi / 3, 5*math.pi / 3, 0, math.pi / 3]
RADIUS_INC = 0.01000000
NO_FLY_ZONE_TYPES = ["hospital", "school", "university", "industrial", "government", "public"]
NO_FLY_ZONE_CLASSES = ["hospital", "school", "university",
                       "library", "public_building", "fire_station", "police", "prison", "courthouse"]


def createConnection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.notification


def generateHexagon(lat, lon, radius):
    lat = float(lat)
    lon = float(lon)
    coordinates = []
    for angle in ANGLES:
        coordinates.append([lon + radius * math.sin(angle),
                           lat + radius * math.cos(angle)])
    return numpy.array(coordinates)


def smallestCircumscribingHexagon(zone):
    # Note: holes are ignored (represented by index > 0)
    coordinates = numpy.array(zone["geometry"]["coordinates"][0])
    center = coordinates.mean(axis=0)
    radius = RADIUS_INC
    while True:
        hexagon = mplPath.Path(generateHexagon(
            center[1], center[0], radius))
        circumscribed = True
        for coordinate in coordinates:
            if hexagon.contains_point(coordinate) == False:
                circumscribed = False
                break
        if circumscribed == True:
            return hexagon.vertices.tolist()
        radius += RADIUS_INC


def main(file, always_avoid):
    notification = createConnection()
    arizona_static = notification.arizona_static

    f = open(file, "r")
    data = json.loads(f.read())
    zones = data["features"]

    types = set()

    for i in range(len(zones)):
        if zones[i]["geometry"]["type"] == "MultiPolygon":
            continue
    
        types.add(zones[i]["properties"]["fclass"])

        # active = False
        # if "type" in zones[i]["properties"] and zones[i]["properties"]["type"] in NO_FLY_ZONE_TYPES:
        #     active = True
        # if zones[i]["properties"]["fclass"] in NO_FLY_ZONE_CLASSES:
        #     active = True

        # properties = {
        #     "EVENT": zones[i]["properties"]["name"],
        #     "GUID": zones[i]["properties"]["osm_id"],
        #     "TYPE": zones[i]["properties"]["code"],
        #     "CLASS": zones[i]["properties"]["fclass"],
        #     "AVOID_START_TIME": datetime.min.isoformat(),
        #     "AVOID_END_TIME": datetime.max.isoformat(),
        #     "ALWAYS_AVOID": 1 if always_avoid else 0,
        #     # "AVOID_CLASS": school/federal building/water 
        # }
        # geometry = {
        #     "type": "Polygon",
        #     "coordinates": [smallestCircumscribingHexagon(zones[i])]
        # }
        # arizona_static.insert_one({
        #     "type": "Feature",
        #     "geometry": geometry,
        #     "properties": properties
        # })
    for type in types:
        if type not in ["college", "school" "university"]:
            print(type)

if __name__ == '__main__':
    main(sys.argv[1], True if (len(sys.argv) ==
         3 and sys.argv[2] == "a") else False)
