# Example usage: python generateHexagon.py 1 1 s
# First argument is latitude of center of hexagon
# Second argument is longitude of center of hexagon
# Third argument is the name of the zone
# Fourth argument should be s if the zone is static, can be ignored otherwise

import pymongo
import sys
import math

CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"
radius = 0.0045
angles = [2*math.pi / 3, math.pi, 4*math.pi / 3, 5*math.pi / 3, 0, math.pi / 3]

def createConnection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.zones

def generateHexagon(lat, lon):
    lat = float(lat)
    lon = float(lon)
    coordinates = []
    for angle in angles:
        coordinates.append((lat + radius * math.cos(angle), lon + radius * math.sin(angle)))
    return coordinates

def insertIntoDB(coordinates, event, static):
    zones = createConnection()
    phoenix = zones.phoenix
    properties = {
        "ALT": 0,
        "EVENT": event,
        "GUID": "GUID",
        "RANGE": 0,
        "SEGMENT": "SEGMENT",
        "TIME": "2022-08-30 16:05:32",
        "TYPE": "GEO",
        "VECTOR": 0,
        "active": 1,
        "class": "FLIGHTCOORIDOR",
        "static": 1 if static else 0
    }
    geometry =  {
        "type": "Polygon",
        "coordinates": [coordinates]
    }
    zone = {
        "type": "CPE_NOTIFICATION_RESP",
        "geometry": geometry,
        "properties": properties
    }
    phoenix.insert_one(zone)

if __name__ == '__main__':
    insertIntoDB(generateHexagon(sys.argv[1], sys.argv[2]), sys.argv[3], True if (len(sys.argv) == 5 and sys.argv[4] == "s") else False)
