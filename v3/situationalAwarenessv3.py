from datetime import datetime, timedelta
# from pydispatch import dispatcher
from bson.json_util import dumps, loads
import json
import pymongo
import argparse
import geopandas as gpd
import math
import numpy as np
import simplekml
import plotly.express as px


"""
BELOW IS THE CODE TO DETERMINE IF A CERTAIN TRAJECTORY IS ENTERING A KEEPOUT ZONE IN REAL-TIME.

SAMPLE COMMANDS TO RUN SCRIPT:
------------------------------
// Version 1: input trajectory JSON, output conflicts
python situationalAwarenessv3.py route1.json
// FALSE output (no zone matches):
>>No conflicts

// TRUE output (some zone match(es):
>>Conflicts listed in conflicts.json

// Version 2: input trajectory JSON with -m flag, displays map with conflicts detected plotted
python situationalAwarenessv3.py route1.json -m
>>Conflicts listed in conflicts.json

// Version 3: No input, output JSON file with list of all the flyable and non-flyable hexagons ("phoenix_zones.json")
python situationalAwarenessv3.py
>>Database dumped to phoenix_zones.json
"""


CONFLICT_SIGNAL = "trajectory-zone-conflict"
CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"
OUT_FILE = "conflicts.geojson"
MAP_FILE = "conflicts_map.geojson"
KML_FILE = "output.kml"


# Retrieve MongoDB database
def getCollection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.notification


# Helper function for intersect
def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


# Return centroid of all vertices
def centroid(vertexes):
    _x_list = [vertex[0] for vertex in vertexes]
    _y_list = [vertex[1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return (_x, _y)


# Return true if hexagon intersects with pair of points
def boolHexagonalLineIntersect(hexagonalCoordinates, p1, p2):
    for i in range(0, len(hexagonalCoordinates) - 1):
        point1 = (hexagonalCoordinates[i][0], hexagonalCoordinates[i][1])
        point2 = (hexagonalCoordinates[i+1][0], hexagonalCoordinates[i+1][1])
        if intersect(p1, p2, point1, point2):
            return True
    return False


# Return true if all hexagon vertices are inside bounding box
def boolHexagonInsideBoundingBox(hexagonalCoordinates, max_bounds, min_bounds):
    points_out_of_bounds = 0
    for i in range(0, len(hexagonalCoordinates) - 1):
        if hexagonalCoordinates[i][0] > max_bounds[0] or hexagonalCoordinates[i][1] > max_bounds[1]:
            points_out_of_bounds += 1
        elif hexagonalCoordinates[i][0] < min_bounds[0] or hexagonalCoordinates[i][1] < min_bounds[1]:
            points_out_of_bounds += 1
    if points_out_of_bounds >= len(hexagonalCoordinates) - 1:
        return False
    return True


# Convert geojson overlay and route file to KML
def geojsonToKML(overlay_file, route_file, kml_file):
    kml = simplekml.Kml()
    # Convert overlay
    with open(overlay_file) as f:
        data = json.load(f)
        for feature in data['features']:
            geom = feature['geometry']
            geom_type = geom['type']
            properties = feature['properties']
            if geom_type == 'Polygon':
                avoid_class = properties['AVOID_CLASS'] if 'AVOID_CLASS' in properties else ''
                event = properties['EVENT'] if properties['EVENT'] != None else properties['CLASS']
                conflicting = properties['conflicting']
                pol = kml.newpolygon(name=avoid_class,
                                    description=event,
                                    outerboundaryis=feature['geometry']['coordinates'][0])
                if avoid_class == 'NotFlyable.Hospital':
                    outline = simplekml.Color.yellow
                elif avoid_class == 'NotFlyable.Tower':
                    if conflicting:
                        outline = simplekml.Color.orange
                    else:
                        outline = simplekml.Color.saddlebrown
                elif avoid_class == 'NotFlyable.Airport':
                    if conflicting:
                        outline = simplekml.Color.red
                    else:
                        outline = simplekml.Color.black
                else:
                    outline = simplekml.Color.grey
                pol.style.linestyle.color = outline
                pol.style.polystyle.color = simplekml.Color.changealphaint(
                    50, outline)
            else:
                print("ERROR: unknown type:", geom_type)
    # Convert trajectory file
    with open(route_file) as f:
        data = json.load(f)
        feature = data['features'][0]
        geom = feature['geometry']
        geom_type = geom['type']
        properties = feature['properties']
        if geom_type == 'LineString':
            pol = kml.newlinestring(name=properties['event'] if 'event' in properties else '',
                                    coords=geom['coordinates'])
            pol.style.linestyle.color = simplekml.Color.darkblue
        else:
            print("ERROR: unknown type:", geom_type)

    kml.save(kml_file)


# Conflict detection
def select_all_tasks(policy_sender, db, trajectory_file):

    f = open(trajectory_file, "r")
    max_bounds = ()
    min_bounds = ()

    # reading from file
    data = json.loads(f.read())
 
    # converting the list of dictionaries from the JSON file to a list of lists
    rows2ListofLists = []
    ref_datetime = datetime.utcnow()
    for i in range(len(data["tsim_s"])):
        rows2ListofLists.append(
            [ref_datetime + timedelta(seconds=data["tsim_s"][i]), (data["longitude_deg"][i], data["latitude_deg"][i])])
        if len(max_bounds) == 0 or len(min_bounds) == 0:
            max_bounds = (data["longitude_deg"][i], data["latitude_deg"][i])
            min_bounds = (data["longitude_deg"][i], data["latitude_deg"][i])
        else:
            max_bounds = (max(data["longitude_deg"][i], max_bounds[0]), max(data["latitude_deg"][i], max_bounds[1]))
            min_bounds = (min(data["longitude_deg"][i], min_bounds[0]), min(data["latitude_deg"][i], min_bounds[1]))

    f.close()
    
    finalIDarray = set()
    conflicts = []
    conflicts_map = []
    route_map = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": []
        },
        "properties": {
            "event": "Trajectory",
            "fclass": "Trajectory",
            "avoid_class": "Trajectory",
            "request_id": [],
            "request_label": [],
            "reference_utc_time": ""
        }
    }
    pois = loads(dumps(db.arizona.find()))
    add_routes = True
    for row in pois:
        if row["properties"]["AVOID_CLASS"][:7] == "Flyable":
            continue

        hexagonalCoordinates = row["geometry"]["coordinates"][0]
        hexagonalCoordinates.append(hexagonalCoordinates[0])
        if not boolHexagonInsideBoundingBox(hexagonalCoordinates, max_bounds, min_bounds):
            continue
        
        start_time = row["properties"]["AVOID_START_TIME"]
        end_time = row["properties"]["AVOID_END_TIME"]
        guid = row["properties"]["GUID"]

        airport_or_tower_added = False

        for i in range(0, len(rows2ListofLists) - 1):

            # storing two consecutive trajectory points
            point1 = [rows2ListofLists[i][1][0], rows2ListofLists[i][1][1]]
            point2 = [rows2ListofLists[i+1][1][0], rows2ListofLists[i+1][1][1]]
            if add_routes:
                route_map["geometry"]["coordinates"].append(point1)

            # storing two consecutive trajectory point times
            time1 = rows2ListofLists[i][0]
            time2 = rows2ListofLists[i + 1][0]

            if (end_time < time1 or start_time > time2):
                continue

            conflicting = boolHexagonalLineIntersect(hexagonalCoordinates, (point1[0], point1[1]), (point2[0], point2[1]))

            row.pop("_id", None)
            row["properties"]["stroke"] = "#ffaa00"
            row["properties"]["stroke-width"] = 2
            row["properties"]["stroke-opacity"] = 1

            # adding the ID of the keepout zone cylinder to the final array if an appropriate intersection is found
            if conflicting:
                if guid not in finalIDarray:
                    finalIDarray.add(guid)
                    # dispatcher.send(signal=CONFLICT_SIGNAL, sender=policy_sender, row=row, time=f"{time1} - {time2}")
                    row["properties"]["conflicting"] = True
                    conflicts_map.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": hexagonalCoordinates
                        },
                        "properties": {
                            "event": row["properties"]["EVENT"],
                            "fclass": row["properties"]["CLASS"],
                            "avoid_class": row["properties"]["AVOID_CLASS"]
                        }
                    })
                    conflicts.append(row)
                    if (row["properties"]["AVOID_CLASS"] == "NotFlyable.Airport" or row["properties"]["AVOID_CLASS"] == "NotFlyable.Tower"):
                        airport_or_tower_added = True
            # always display airports/airfields/helipads and towers
            elif (row["properties"]["AVOID_CLASS"] == "NotFlyable.Airport" or row["properties"]["AVOID_CLASS"] == "NotFlyable.Tower"):
                if not airport_or_tower_added:
                    hexagonalCoordinates.append(hexagonalCoordinates[0])
                    row["properties"]["conflicting"] = False
                    conflicts.append(row)
                    airport_or_tower_added = True
            
        add_routes = False

    route_map["geometry"]["coordinates"].append([rows2ListofLists[len(rows2ListofLists) - 1]
                     [1][0], rows2ListofLists[len(rows2ListofLists) - 1][1][1]])
    conflicts_map.append(route_map)

    with open(OUT_FILE, "w") as outfile:
        conflicts_list = {
            "type": "FeatureCollection",
            "features": conflicts
        }
        outfile.write(dumps(conflicts_list, indent=4))

    with open(MAP_FILE, "w") as outfile:
        conflicts_map = {
            "type": "FeatureCollection",
            "features": conflicts_map
        }
        outfile.write(dumps(conflicts_map, indent=4))

    route_file = trajectory_file[:trajectory_file.index(".")] + ".geojson"
    with open(route_file, "w") as outfile:
        route_map = {
            "type": "FeatureCollection",
            "features": [route_map]
        }
        outfile.write(dumps(route_map, indent=4))


    return finalIDarray


# Return dump of database
def get_zones(db):
    with open("phoenix_zones.json", "w") as outfile:
        outfile.write(dumps(list(db.arizona.find()), indent=4))


# def trajectory_service(sender, row, time):
#     print(f"{sender}: Trajectory has a conflict with following zone from {time}: \n ==================================== \n {row}")


def mainBuildRegion():
    policy_sender = object()
    # dispatcher.connect(trajectory_service, signal=CONFLICT_SIGNAL, sender=dispatcher.Any)
    parser = argparse.ArgumentParser(
        description="This program takes in a json trajectory route and identifies conflicts between the trajectory and a POI database"
        )
    parser.add_argument("filename", nargs="*", default=["-"])
    parser.add_argument("-m", action="store_true")
    args = parser.parse_args()

    zones = getCollection()
    if args.filename[0] == "-":
        get_zones(zones)
        print("Database dumped to phoenix_zones.json")
    else:
        conflicts = select_all_tasks(
            policy_sender, zones, args.filename[0])
        print("No conflicts" if len(conflicts) == 0 else "Conflicts listed in", OUT_FILE)
        if args.m:
            conflicts = gpd.read_file(MAP_FILE)
            lats = []
            lons = []
            names = []
            avoid_classes = []

            for feature, event, fclass, avoid_class in zip(conflicts.geometry, conflicts.event, conflicts.fclass, conflicts.avoid_class):
                linestrings = [feature]
                for linestring in linestrings:
                    x, y = linestring.xy
                    lats = np.append(lats, y)
                    lons = np.append(lons, x)
                    names = np.append(names, [event if event else fclass]*len(y))
                    avoid_classes = np.append(avoid_classes, [avoid_class]*len(y))
                    lats = np.append(lats, None)
                    lons = np.append(lons, None)
                    names = np.append(names, None)
                    avoid_classes = np.append(avoid_classes, None)

            color_sequence = ["#FF2D00", "#FF9200", "#FFF300", "#0015FF"]
            fig = px.line_mapbox(lat=lats, lon=lons, hover_name=names,
                                 mapbox_style="stamen-terrain", color=avoid_classes,
                                 color_discrete_sequence=color_sequence)
            fig.update_layout(mapbox_zoom=10, mapbox_center_lat=33.37)
            fig.show()

    route_file = args.filename[0][:args.filename[0].index(".")] + ".geojson"
    geojsonToKML(OUT_FILE, route_file, KML_FILE)
    print("KML file: ", KML_FILE)
    print("Route file: ", route_file)


if __name__ == "__main__":
    mainBuildRegion()
    
    
