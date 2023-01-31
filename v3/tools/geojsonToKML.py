import simplekml
import json
import argparse

OUT_FILE = "../conflicts_map.kml"

parser = argparse.ArgumentParser(
    description="This program takes in a json trajectory route and identifies conflicts between the trajectory and a POI database"
)
parser.add_argument("filename", nargs="*")
args = parser.parse_args()

with open(args.filename[0]) as f:
    data = json.load(f)
    kml = simplekml.Kml()
    for feature in data['features']:
        geom = feature['geometry']
        geom_type = geom['type']
        properties = feature['properties']
        if geom_type == 'LineString':
            kml.newlinestring(name=properties['avoid_class'],
                            description=properties['event'],
                            coords=geom['coordinates'])
        else:
            print("ERROR: unknown type:", geom_type)
kml.save(OUT_FILE)
