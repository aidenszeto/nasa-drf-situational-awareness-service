from datetime import datetime
from pydispatch import dispatcher
from bson.json_util import dumps, loads
import json
import pymongo
import sys

CONFLICT_SIGNAL = 'trajectory-zone-conflict'
CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"

'''
BELOW IS THE CODE TO DETERMINE IF A CERTAIN TRAJECTORY IS ENTERING A KEEPOUT ZONE IN REAL-TIME.

SAMPLE COMMANDS TO RUN SCRIPT:
------------------------------
// Version 1: input trajectory JSON, output conflicts
python situationalAwarenessv3.py trajectory_request_geo.json
// FALSE output (no zone matches):
>>[]

// TRUE output (some zone match(es):
>><object object at 0x7f9c68d14f00>: Trajectory has a conflict with following zone from 2022-08-30 16:00:32 - 2022-08-30 16:10:32: 
 ==================================== 
 {"type": "CPE_NOTIFICATION_RESP", "geometry": {"type": "Polygon", "coordinates": [[[1, 1], [3, 3], [-112.07487793157966, 33.35969
 573361516], [-112.1154646018878, 33.37213303894667], [-112.14910880414443, 33.34917391297312], [-112.14216470823824, 33.313784835
 21286], [-112.10159788091084, 33.30135043883555]]]}, "properties": {"TIME": "2022-08-30 16:05:32", "TYPE": "GEO", "EVENT": "EMSAL
 ERT", "GUID": "GUID", "SEGMENT": "SEGMENT", "RANGE": 0, "VECTOR": 0, "ALT": 0, "class": "FLIGHTCOORIDOR"}}
['GUID']

// Version 2: no input, output JSON file with list of all the flyable and non-flyable hexagons ("phoenix_zones.json")
python situationalAwarenessv3.py
>>[{'_id': ObjectId('63491476cf751ad7ed637ff1'), 'type': 'example', 'geometry': {'type': 'Polygon', 'coordinates': [[[1, 1], [3, 3
], [-112.07487793157966, 33.35969573361516], [-112.1154646018878, 33.37213303894667], [-112.14910880414443, 33.34917391297312], [-
112.14216470823824, 33.31378483521286], [-112.10159788091084, 33.30135043883555]]]}, 'properties': {'ALT': 0, 'EVENT': 'EMSALERT',
 'GUID': 'GUID', 'RANGE': 0, 'SEGMENT': 'SEGMENT', 'TIME': '2022-08-30 16:05:32', 'TYPE': 'GEO', 'VECTOR': 0, 'active': 1, 'class':
  'FLIGHTCOORIDOR', 'static': 0}}, ...
'''

def getCollection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.zones

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def boolHexagonalLineIntersect(hexagonalCoordinates, p1, p2):
    for i in range(0, len(hexagonalCoordinates) - 1):
        point1 = (hexagonalCoordinates[i][0], hexagonalCoordinates[i][1])
        point2 = (hexagonalCoordinates[i+1][0], hexagonalCoordinates[i+1][1])
        if intersect(p1, p2, point1, point2):
            return True
    return False

def select_all_tasks(policy_sender, db, trajectory_file):

    f = open(trajectory_file, "r")

    rows2ListofLists = []  
    # reading from file
    data = json.loads(f.read())
 
    # converting the list of dictionaries from the JSON file to a list of lists
    rows2ListofLists = []
    for i in range(len(data['tsim_datetime'])):
        rows2ListofLists.append(
            [data['tsim_datetime'][i], (data['latitude_deg'][i], data['longitude_deg'][i])])

    f.close()
    
    # empty array that will return upon no intersectfstion
    finalIDarray = []
    
    # trajectory-line loop
    for i in range(0, len(rows2ListofLists) - 1):

        # storing two consecutive trajectory points
        point1 = [rows2ListofLists[i][1][0], rows2ListofLists[i][1][1]]
        point2 = [rows2ListofLists[i+1][1][0], rows2ListofLists[i+1][1][1]]
        
        # storing two consecutive trajectory point times
        time1 = datetime.strptime(
            rows2ListofLists[i][0], '%Y-%m-%d %H:%M:%S')
        time2 = datetime.strptime(
            rows2ListofLists[i + 1][0], '%Y-%m-%d %H:%M:%S')
        
        # list of inactive zones at current time of request
        rows1 = loads(dumps(db.phoenix.find()))

        for row in rows1:
            if not row['properties']['static'] and not row['properties']['active']:
                break
            time = datetime.strptime(
                row['properties']['TIME'], '%Y-%m-%d %H:%M:%S')
            if (time < time1 or time > time2):
                continue

            guid = row['properties']['GUID']
            hexagonalCoordinates = row['geometry']['coordinates'][0]

            boolVal = boolHexagonalLineIntersect(hexagonalCoordinates, (point1[0], point1[1]), (point2[0], point2[1]))
            # adding the ID of the keepout zone cylinder to the final array if an appropriate intersection is found
            if (boolVal == True):
                finalIDarray.append(guid)
                dispatcher.send(signal=CONFLICT_SIGNAL, sender=policy_sender, row=row, time=f'{time1} - {time2}')
                
            # removing potential duplicates when two line segments fall within the same cylinder
            finalIDarray = list(dict.fromkeys(finalIDarray))
                
    # returning final list of ID(s), if any      
    return (finalIDarray)           

def get_zones(db):
    with open("phoenix_zones.json", "w") as outfile:
        outfile.write(dumps(list(db.phoenix.find()), indent=4))

def trajectory_service(sender, row, time):
    print(f'{sender}: Trajectory has a conflict with following zone from {time}: \n ==================================== \n {row}')

def mainBuildRegion():
    policy_sender = object()
    dispatcher.connect(trajectory_service, signal=CONFLICT_SIGNAL, sender=dispatcher.Any)
    zones = getCollection()
    if (len(sys.argv) > 1):
        conflicts = select_all_tasks(
            policy_sender, zones, sys.argv[1])
        print("No conflicts" if len(conflicts) == 0 else conflicts)
    else:
        get_zones(zones)
    
if __name__ == '__main__':
    mainBuildRegion()
    
    
