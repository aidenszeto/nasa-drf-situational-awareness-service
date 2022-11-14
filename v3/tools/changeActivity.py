# Example usage: python changeActivity.py 6349e1ce1ba6ad8f0a381c4d 0
# First argument is ObjectId from MongoDB
# Second argument is value to set for active field

import pymongo
import sys
from bson.objectid import ObjectId

CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"

def createConnection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.zones

def main(oid, active):
    active = int(active)
    assert (active == 0 or active == 1)
    assert (isinstance(oid, str))
    zones = createConnection()
    phoenix = zones.phoenix
    filter = {
        "_id": ObjectId(oid)
    }
    doc = phoenix.find_one(filter)
    if doc and not doc['properties']['static']:
        phoenix.update_one(filter, {
            "$set": {
                "properties.active": active
            }
        })
    else:
        print('Invalid objectId or zone is static')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
