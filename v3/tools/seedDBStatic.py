# First argument is the name of the geojson file to upload
# Second argument is a if the file contains zones that are always avoided
# 
# python3 seedDBStatic.py arizona-geojson/gis_osm_pois_a_free_1.geojson -a --> zones always avoid
# python3 seedDBStatic.py arizona-geojson/gis_osm_pois_a_free_1.geojson --> zones not always avoid

import pymongo
import sys
import json
import numpy
import math
import matplotlib.path as mplPath
import argparse
from datetime import datetime
from classes.classes import Water, School, Government, Hospital, Health, Retail, Entertainment, Outdoors, Food, Housing, Service, Tower, Airport, Bus


CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"
ANGLES = [2*math.pi / 3, math.pi, 4*math.pi / 3, 5*math.pi / 3, 0, math.pi / 3]
RADIUS_INC = 0.01000000
DATABASE = "california"


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


def main(file, always_avoid, store_flyable):
    nsdb = createConnection()
    if DATABASE == "arizona":
        if store_flyable:
            col = nsdb.arizona_static
        else:
            col = nsdb.arizona
    elif DATABASE == "california":
        if store_flyable:
            col = nsdb.california_static
        else:
            col = nsdb.california
    else:
        print("ERROR: database collection not found")
        return

    f = open(file, "r")
    data = json.loads(f.read())
    zones = data["features"]

    types = set()

    for i in range(len(zones)):
        if zones[i]["geometry"]["type"] == "MultiPolygon":
            continue
    
        types.add(zones[i]["properties"]["fclass"])

        fclass = zones[i]["properties"]["fclass"]
        if fclass in Water:
            fclass = "Flyable.Water"
        elif fclass in School:
            fclass = "Flyable.School"
        elif fclass in Government:
            fclass = "Flyable.Government"
        elif fclass in Tower:
            fclass = "NotFlyable.Tower"
        elif fclass in Service:
            fclass = "Flyable.Service"
        elif fclass in Hospital:
            fclass = "NotFlyable.Hospital"
        elif fclass in Health:
            fclass = "Flyable.Health"
        elif fclass in Retail:
            fclass = "Flyable.Retail"
        elif fclass in Entertainment:
            fclass = "Flyable.Entertainment"
        elif fclass in Outdoors:
            fclass = "Flyable.Outdoors"
        elif fclass in Food:
            fclass = "Flyable.Food"
        elif fclass in Housing:
            fclass = "Flyable.Housing"
        elif fclass in Airport:
            fclass = "NotFlyable.Airport"
        elif fclass in Bus:
            fclass = "Flyable.Bus"
        else:
            fclass = "Flyable.Misc"

        properties = {
            "EVENT": zones[i]["properties"]["name"],
            "GUID": zones[i]["properties"]["osm_id"],
            "TYPE": zones[i]["properties"]["code"],
            "CLASS": zones[i]["properties"]["fclass"],
            "AVOID_START_TIME": datetime.min,
            "AVOID_END_TIME": datetime.max,
            "ALWAYS_AVOID": 1 if always_avoid else 0,
            "AVOID_CLASS": fclass
        }
        geometry = {
            "type": "Polygon",
            "coordinates": [smallestCircumscribingHexagon(zones[i])]
        }
        if fclass[:3] == "Not":
            col.insert_one({
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            })
        else:
            if store_flyable:
                col.insert_one({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": properties
                })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="This program takes in a geojson file containing POIs and seeds a database with fly or no-fly zones"
    )
    parser.add_argument("filename", nargs=1)
    parser.add_argument("-a", action="store_true")
    parser.add_argument("-f", action="store_true")
    args = parser.parse_args()

    main(args.filename[0], args.a, args.f)