# This script takes shape objects from the arizona-latest-free.shp directory found here
# (http://download.geofabrik.de/north-america/us/arizona.html) and makes a directory
# arizona-geojson containing the shp files converted to geojson format

import os
import geopandas as gp

DIRECTORY = "arizona-latest-free.shp"

def main():
    for filename in os.listdir(DIRECTORY):
        f = os.path.join(DIRECTORY, filename)
        if os.path.isfile(f) and f[len(f) - 4:] == ".shp":
            data = gp.read_file(f)
            df = gp.GeoDataFrame(data)
            df.to_file(
                f"arizona-geojson/{f[len(DIRECTORY) + 1:len(f) - 4]}.geojson", driver="GeoJSON")


if __name__ == '__main__':
    main()
