import simplekml
import json
import argparse

"""
EXAMPLE: python3 tools/geojsonToKML.py conflicts.geojson route1.geojson
"""

OUT_FILE = "output.kml"

parser = argparse.ArgumentParser(
    description="This program takes in a json trajectory route and identifies conflicts between the trajectory and a POI database"
)
parser.add_argument("files", nargs="*")
args = parser.parse_args()
kml = simplekml.Kml()

# Convert overlay
with open(args.files[0]) as f:
    data = json.load(f)
    for feature in data['features']:
        geom = feature['geometry']
        geom_type = geom['type']
        properties = feature['properties']
        if geom_type == 'LineString':
            kml.newlinestring(name=properties['event'] if 'event' in properties else '',
                              coords=geom['coordinates'])
        elif geom_type == 'Polygon':
            avoid_class = properties['AVOID_CLASS'] if 'AVOID_CLASS' in properties else ''
            event = properties['EVENT'] if 'EVENT' in properties else ''
            pol = kml.newpolygon(name=avoid_class,
                           description=event,
                           outerboundaryis=feature['geometry']['coordinates'][0])
            if avoid_class == 'NotFlyable.Hospital':
                outline = simplekml.Color.yellow
            elif avoid_class == 'NotFlyable.Tower':
                outline = simplekml.Color.orange
            elif avoid_class == 'NotFlyable.Airport':
                outline = simplekml.Color.red
            else:
                outline = simplekml.Color.grey
            pol.style.linestyle.color = outline
            pol.style.polystyle.color = simplekml.Color.changealphaint(
                75, outline)
        else:
            print("ERROR: unknown type:", geom_type)

# Convert trajectory file
with open(args.files[1]) as f:
    data = json.load(f)
    feature = data['features']
    geom = feature['geometry']
    geom_type = geom['type']
    properties = feature['properties']
    if geom_type == 'LineString':
        pol = kml.newlinestring(name=properties['event'] if 'event' in properties else '',
                            coords=geom['coordinates'])
        pol.style.linestyle.color = simplekml.Color.darkblue
    else:
        print("ERROR: unknown type:", geom_type)

kml.save(OUT_FILE)
