# This script takes shape objects from the arizona-latest-free.shp directory found here
# (http://download.geofabrik.de/north-america/us/arizona.html) and makes a directory
# arizona-geojson containing the shp files converted to geojson format

import os
import geopandas as gp
import argparse

def main(shp_dir, new_dir):
    for filename in os.listdir(shp_dir):
        f = os.path.join(shp_dir, filename)
        if os.path.isfile(f) and f[len(f) - 4:] == ".shp":
            data = gp.read_file(f)
            df = gp.GeoDataFrame(data)
            df.to_file(
                f"{new_dir}/{f[len(shp_dir) + 1:len(f) - 4]}.geojson", driver="GeoJSON")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="This program takes in a directory of .shp files and converts them to .geojson"
    )
    parser.add_argument("directory", nargs="*")
    args = parser.parse_args()
    shp_dir = args.directory[0]
    new_dir = shp_dir[:shp_dir.index("-")] + "-geojson"
    main(shp_dir, new_dir)
