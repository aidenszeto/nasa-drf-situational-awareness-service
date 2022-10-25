import sys
import math
import sqlite3
from sqlite3 import Error
from pydispatch import dispatcher
import json

CONFLICT_SIGNAL = 'trajectory-zone-conflict'

'''
BELOW IS THE CODE TO DETERMINE IF A CERTAIN TRAJECTORY IS ENTERING A KEEPOUT ZONE IN REAL-TIME.

SAMPLE COMMANDS TO RUN SCRIPT:
------------------------------

python situationalAwareness.py
FALSE output (no cylinder ID matches):
>>[]

TRUE output (some cylinder ID match(es):
>>[6,3]

'''
# connecting to database

def create_connection(test1):
    conn = None
    try:
        conn = sqlite3.connect(test1)
    except Error as e:
        print(e)
    
    return conn
  
# testing the database calls

def boolcylinderLineIntersect(heightOfKeepout, radiusOfKeepout, xKeepoutBottom, yKeepoutBottom, zKeepoutBottom, point1, point2):

    # info on given base center

    xKeepoutTop = xKeepoutBottom
    yKeepoutTop = yKeepoutBottom
    zKeepoutTop = zKeepoutBottom + heightOfKeepout


    p = (xKeepoutTop - xKeepoutBottom)**2 + (yKeepoutTop - yKeepoutBottom)**2 + (zKeepoutTop - zKeepoutBottom)**2


    # info on trajectory between two points
    
    xCoord1 = point1[0]
    yCoord1 = point1[1]
    zCoord1 = point1[2]

    xCoord2 = (point2[0])
    yCoord2 = (point2[1])
    zCoord2 = (point2[2])
    

    # returning true if any of the trajectory points match exactly with the keepout cylinder base
    if (xCoord1 == xKeepoutBottom and yCoord1 == yKeepoutBottom and zCoord1 == zKeepoutBottom):
        return True
    if (xCoord2 == xKeepoutBottom and yCoord2 == yKeepoutBottom and zCoord2 == zKeepoutBottom):
        return True

    # assigning values to the top-most and bottom-most potential values of the height
    if (zCoord1 < zCoord2):
        lowestZCoord = zCoord1
        highestZCoord = zCoord2
    else:
        lowestZCoord = zCoord2
        highestZCoord = zCoord1
        
    # checking if the trajectory height falls within the keepout zone height
        
    if (lowestZCoord < zKeepoutBottom or lowestZCoord > zKeepoutTop or highestZCoord < zKeepoutBottom or highestZCoord > zKeepoutTop):

        #print("There is no intersection between the line and cylinder; height of trajectory is out of bounds.")
        result = False
        
    else:

        a = xCoord1
        b = yCoord1
        c = zCoord1

        # calculating change in coordinates
        deltaX = xCoord2 - xCoord1
        deltaY = yCoord2 - yCoord1
        deltaZ = zCoord2 - zCoord1

        d = deltaX
        e = deltaY
        f = deltaZ

        l = xKeepoutBottom
        m = yKeepoutBottom
        n = zKeepoutBottom

        # calculating the intersection points between the cylinder of the keepout zone and the line of the trajectory's two adjacent points
        
        try:

            tNumerator1 = -4*e*b-2*n*b+2*m*b+2*e*c+2*n*c-2*l*c+2*l*a+2*e*a-2*m*a+2*c*d-4*a*d+2*b*d+2*b*f-4*c*f+2*a*f+math.sqrt((4*e*b+2*n*b-2*m*b-2*e*c-2*n*c+2*l*c-2*l*a-2*e*a+2*m*a-2*c*d+4*a*d-2*b*d-2*b*f+4*c*f-2*a*f)**2-4*(2*b**2+2*c**2-2*b*c+2*a**2-2*c*a-2*b*a)*(2*e**2+n**2+2*e*n+l**2+m**2-2*e*m+2*d**2-2*l*d-2*e*d+2*m*d+2*f**2-2*e*f-2*n*f-2*d*f+2*l*f-p*radiusOfKeepout**2))
            tDenominator = 2*(2*b**2+2*c**2-2*b*c+2*a**2-2*c*a-2*b*a)
            
            # first intersection point, if any
            tFinal1 = tNumerator1/tDenominator
            
            # parameterization of the equation of a line
        
            lineEquationX1 = xCoord1*tFinal1 + deltaX
            lineEquationY1 = yCoord1*tFinal1 + deltaY
            lineEquationZ1 = zCoord1*tFinal1 + deltaZ
       
            intersection1 = [lineEquationX1, lineEquationY1, lineEquationZ1]
       
            #print("Intersection #1 is at: " + str(intersection1))
            result = True
            return True
        
        # catching dividing by zero when the line is parallel to the cylinder and lies exactly on it
        except ZeroDivisionError:
            
            #print("Intersects infintely many times.")
            result = True
            return True
            
        # no intersection when it fails all cases
        except:
        
            #print("There is no intersection between the line and cylinder.")
            result = False
              
        # trying for a second intersection between the keepout cylinder and trajectory line segment
        try:
            tNumerator2 = -4*e*b-2*n*b+2*m*b+2*e*c+2*n*c-2*l*c+2*l*a+2*e*a-2*m*a+2*c*d-4*a*d+2*b*d+2*b*f-4*c*f+2*a*f-math.sqrt((4*e*b+2*n*b-2*m*b-2*e*c-2*n*c+2*l*c-2*l*a-2*e*a+2*m*a-2*c*d+4*a*d-2*b*d-2*b*f+4*c*f-2*a*f)**2-4*(2*b**2+2*c**2-2*b*c+2*a**2-2*c*a-2*b*a)*(2*e**2+n**2+2*e*n+l**2+m**2-2*e*m+2*d**2-2*l*d-2*e*d+2*m*d+2*f**2-2*e*f-2*n*f-2*d*f+2*l*f-p*radiusOfKeepout**2))
            tDenominator = 2*(2*b**2+2*c**2-2*b*c+2*a**2-2*c*a-2*b*a)
            
            # second intersection value
            tFinal2 = tNumerator2/tDenominator
        
            lineEquationX2 = xCoord1*tFinal2 + deltaX
            lineEquationY2 = yCoord1*tFinal2 + deltaY
            lineEquationZ2 = zCoord1*tFinal2 + deltaZ
            
            # second intersection point
            intersection2 = [lineEquationX2, lineEquationY2, lineEquationZ2]
        
            #print("Intersection #2 is at: " + str(intersection2))
            result = True
            return True
            
        # catching dividing by zero when the line is parallel to the cylinder and lies exactly on it
        except ZeroDivisionError:

            #print("Intersects infintely many times.")
            result = True
            return True
         
        # no intersection when it fails all cases
        except:

            #print("There is no intersection between the line and cylinder.")
            result = False
        
    # returning false if the temporary value of the result has not exited the function yet
    if (result == False):
        return False


def select_all_tasks(policy_sender):

    ''' 
    # CODE TO USE SQL INSTEAD OF JSON:
    curBuild2 = conn.cursor()
    selectStatement2 = "SELECT xTrajectory,yTrajectory,zTrajectory, Time FROM Trajectory"
    curBuild2.execute(selectStatement2)
    
    rows2Tuple = list(curBuild2)    
    rows2ListofLists = [list(i) for i in rows2Tuple]
    #print(rows2ListofLists)
    '''
    
    # CODE TO USE JSON INSTEAD OF SQL:
    f = open('TrajectoryData_example1.json', "r")
    # f = open ('NorthernPhoenixRoute.json', "r")
    # f = open ('WesternPhoenixRoute.json', "r")
    # f = open ('trajectoryJSON.json', "r")

    rows2ListofLists = []  
    # reading from file
    data = json.loads(f.read())
 
    # converting the list of dictionaries from the JSON file to a list of lists
    for i in range(len(data['tsim_s'])):
        rows2ListofLists.append([data['latitude_deg'][i], data['longitude_deg'][i], data['h_ft'][i], data['tsim_s'][i]])
    # for i in data:   
    #     rows2ListofLists.append([i['xTrajectory'], i['yTrajectory'], i['zTrajectory'], i['Time']])

    f.close()
    
    # empty array that will return upon no intersection
    finalIDarray = []
    
    # trajectory-line loop
    for i in range(0, len(rows2ListofLists) - 1):

        # storing two consecutive trajectory points
        point1 = [rows2ListofLists[i][0], rows2ListofLists[i][1], rows2ListofLists[i][2]]
        point2 = [rows2ListofLists[i+1][0], rows2ListofLists[i+1][1], rows2ListofLists[i+1][2]]
        
        # storing two consecutive trajectory point times
        time1 = rows2ListofLists[i][3]
        time2 = rows2ListofLists[i+1][3]
        
        # # database call to fetch required columns
        # curBuild = conn.cursor()
        
        # # checks that the status is active and that the time of the maintenance period falls under some time of the trajectory
        # selectStatement = "SELECT xCoordinate,yCoordinate,zCoordinate,Impact,ID FROM EmergencyNotification WHERE (datetime('{}') >= datetime(Time) and datetime('{}') <= datetime(Time, '+' || Validity || ' minutes') or datetime('{}') >= datetime(Time) and datetime('{}') <= datetime(Time, '+' || Validity || ' minutes')) or (datetime(Time) >= datetime('{}') and datetime(Time, '+' || Validity || ' minutes') <= datetime('{}') or (datetime(Time) >= datetime('{}') and datetime(Time, '+' || Validity || ' minutes') <= datetime('{}'))) and Status = 'Active'".format(time1,time1,time2,time2,time1,time1,time2,time2)

        # curBuild.execute(selectStatement)

        # # collecting the rows 
        # rows1 = curBuild.fetchall()

        f = open('PolicyData_example1.json', "r")
        rows1 = json.loads(f.read())

        # cylinder loop
        for row in rows1:

            # checking validity of policy zone
            time = row['Time']
            validity = row['Validity']
            status = row['Status']
            if status == 'Inactive':
                continue

            if ((time1 >= time and time1 <= time + validity or time2 >= time and time2 <= time + validity) 
                    or (time >= time1 and time + validity <= time1 or time >= time2 and time + validity <= time2)):
                continue

            # storing the values from the database
            xKeepoutBottom = row['xCoordinate']
            yKeepoutBottom = row['yCoordinate']
            zKeepoutBottom = row['zCoordinate']
            impact = row['Impact']
            cylinderID = row['ID']

            # calculating the radius and height of the keepout zone given the extent of damage
            radiusOfKeepout = -0.0795*(impact)**2 + 6.9356*(impact) - 3.4833
            heightOfKeepout = -0.6136*(impact)**2 + 13.356*(impact) - 12.333

            # recursive function call to determine if there is an intersection between keepout cylinder and line and where
            boolVal = (boolcylinderLineIntersect(heightOfKeepout, radiusOfKeepout, xKeepoutBottom, yKeepoutBottom, zKeepoutBottom, point1, point2))                   
      
            # adding the ID of the keepout zone cylinder to the final array if an appropriate intersection is found
            if (boolVal == True):
                finalIDarray.append(cylinderID)
                dispatcher.send(signal=CONFLICT_SIGNAL, sender=policy_sender, zone_id=cylinderID, time=f'{time1} - {time2}')
                
            # removing potential duplicates when two line segments fall within the same cylinder
            finalIDarray = list(dict.fromkeys(finalIDarray))
                
    # returning final list of ID(s), if any      
    return (finalIDarray)           

def trajectory_service(sender, zone_id, time):
    print(f'{sender}: Trajectory has a conflict with zone {zone_id} from {time}')

def mainBuildRegion():
    policy_sender = object()
    dispatcher.connect(trajectory_service, signal=CONFLICT_SIGNAL, sender=dispatcher.Any)
    print(select_all_tasks(policy_sender))

    # # please modify path to database as needed
    # database = r"\\\\wsl.localhost\\Ubuntu\\home\\aiden\\nasa\\arc-aft\\test1.db"

    # # create a database connection
    # conn = create_connection(database)
    # with conn:
    #     #print("1. Query task by priority:")
    #     #select_task_by_priority(conn, 1)

    #     #print("2. Query all tasks")
    #     print((select_all_tasks(conn)))


    
if __name__ == '__main__':
    mainBuildRegion()
    
    
