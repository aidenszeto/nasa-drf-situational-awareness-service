import sys
import math
from sqlite3 import Error
from pydispatch import dispatcher
import json

CONFLICT_SIGNAL = 'trajectory-zone-conflict'

'''
BELOW IS THE CODE TO DETERMINE IF A CERTAIN TRAJECTORY IS ENTERING A KEEPOUT ZONE IN REAL-TIME.

SAMPLE COMMANDS TO RUN SCRIPT:
------------------------------

python situationalAwareness.py
FALSE output (no zone matches):
>>[]

TRUE output (some zone match(es):
>>[6,3]

'''


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

def select_all_tasks(policy_sender):
    
    # CODE TO USE JSON INSTEAD OF SQL:
    f = open('trajectory_request_geo.json', "r")
    # f = open ('NorthernPhoenixRoute.json', "r")
    # f = open ('WesternPhoenixRoute.json', "r")
    # f = open ('trajectoryJSON.json', "r")

    rows2ListofLists = []  
    # reading from file
    data = json.loads(f.read())
 
    # converting the list of dictionaries from the JSON file to a list of lists
    rows2ListofLists = [data['properties']['starttime'], data['properties']['endtime'], data['geometry']['coordinates']]
    f.close()
    
    # empty array that will return upon no intersection
    finalIDarray = []
    
    # trajectory-line loop
    coordinates = rows2ListofLists[2]
    total_time = rows2ListofLists[1] - rows2ListofLists[0]
    tsim_s = total_time / (len(coordinates) - 1)
    curr_time = 0
    for i in range(0, len(coordinates) - 1):

        # storing two consecutive trajectory points
        point1 = [coordinates[i][0], coordinates[i][1]]
        point2 = [coordinates[i+1][0], coordinates[i+1][1]]
        
        # storing two consecutive trajectory point times
        time1 = curr_time
        curr_time += tsim_s
        time2 = curr_time
        
        # list of inactive zones at current time of request
        f = open('policy_response_geo.json', "r")
        rows1 = json.loads(f.read())

        for row in rows1:
            time = row['properties']['TIME']
            if (time < time1 or time > time2):
                continue

            guid = row['properties']['GUID']
            hexagonalCoordinates = row['geometry']['coordinates'][0]

            boolVal = boolHexagonalLineIntersect(hexagonalCoordinates, (point1[0], point1[1]), (point2[0], point2[1]))
            # adding the ID of the keepout zone cylinder to the final array if an appropriate intersection is found
            if (boolVal == True):
                finalIDarray.append(guid)
                dispatcher.send(signal=CONFLICT_SIGNAL, sender=policy_sender, row=json.dumps(row), time=f'{time1} - {time2}')
                
            # removing potential duplicates when two line segments fall within the same cylinder
            finalIDarray = list(dict.fromkeys(finalIDarray))
                
    # returning final list of ID(s), if any      
    return (finalIDarray)           

def trajectory_service(sender, row, time):
    print(f'{sender}: Trajectory has a conflict with following zone from {time}: \n ==================================== \n {row}')

def mainBuildRegion():
    policy_sender = object()
    dispatcher.connect(trajectory_service, signal=CONFLICT_SIGNAL, sender=dispatcher.Any)
    print(select_all_tasks(policy_sender))
    
if __name__ == '__main__':
    mainBuildRegion()
    
    
