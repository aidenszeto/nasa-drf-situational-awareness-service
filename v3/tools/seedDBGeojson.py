# First argument is the name of the geojson file
# Scond argument is s for if zones are static

import pymongo
import sys
import json
import numpy
import math
import matplotlib.path as mplPath
import geopandas as gp


CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"
ANGLES = [2*math.pi / 3, math.pi, 4*math.pi / 3, 5*math.pi / 3, 0, math.pi / 3]
RADIUS_INC = 0.01000000


def createConnection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.notification


def generateHexagon(lat, lon, radius):
    print((lat, lon))
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
            return list(hexagon.vertices)
            break
        radius += RADIUS_INC


def main(file, static):
    notification = createConnection()
    arizona = notification.arizona

    f = open(file, "r")
    data = json.loads(f.read())
    zones = data["features"]

    for i in range(len(zones)):
        properties = {
            "EVENT": zones[i]["properties"]["name"],
            "GUID": zones[i]["properties"]["osm_id"],
            "TYPE": zones[i]["properties"]["code"],
            "active": 1,
            "class": zones[i]["properties"]["fclass"],
            "static": 1 if static else 0
        }
        geometry = {
            "type": "Polygon",
            "coordinates": [smallestCircumscribingHexagon(zones[i])]
        }
        # print({
        #     "type": "Feature",
        #     "geometry": geometry,
        #     "properties": properties
        # })
        # arizona.insert_one({
        #     "type": "Feature",
        #     "geometry": geometry,
        #     "properties": properties
        # })


if __name__ == '__main__':
    main(sys.argv[1], True if (len(sys.argv) ==
         3 and sys.argv[2] == "s") else False)
