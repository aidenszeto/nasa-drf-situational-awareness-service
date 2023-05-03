# NASA DRF Situational Awareness Service
The situational awareness script takes in a given geojson trajectory and identifies trajectory conflicts against a given POI database. The script generates an output.kml file that visualizes all of the conflicting POIs (with [Google Earth](https://support.google.com/earth/answer/7365595?hl=en&co=GENIE.Platform%3DDesktop)).

### Adding support for additional regions
This service uses open source POI data to seed a [MongoDB database](https://cloud.mongodb.com/v2/633f0c6a0a2ec54e54c12722#/metrics/replicaSet/633f0c824d223445f445fa6e/explorer/nsdb/az/find). To seed the database with data from a new region:

 - Download the _.shp.zip_ file for the region from [Geofabrik](https://download.geofabrik.de/north-america/us.html).
 - Unzip the file. You should now have a folder called __REGION_NAME-latest-free.shp__.
 - Run `python v3/tools/shpToGeojson.py REGION_NAME-latest-free.shp`, replacing REGION_NAME with the actual region name of the _.shp_ file.
 - This should make a new folder called __REGION_NAME-geojson__ which contains geojson files for various POI types. We want to use __gis_osm_pois_a_free_1.geojson__ and __gis_osm_water_a_free_1.geojson__.
 - In _v3/tools/seedDBStatic.py_, update line 21 to refer to your region name. For example, if we are seeding data for New York we could replace `ca` with `ny`
 - Run the following commands to seed the database
   - General POIs: `python v3/tools/seedDBStatic.py REGION_NAME-geojson/gis_osm_pois_a_free_1.geojson -f`
   - Bodies of water: `python v3/tools/seedDBStatic.py REGION_NAME-geojson/gis_osm_water_a_free_1.geojson -f`

__Note:__ The -f flag can be removed if you would not like to store flyable POIs. If -f is set, the seedDBStatic.py script will store all POIs. If you would like to store a version of the data with the flyable POIs and a version without the flyable POIs you should use different database names, ie. `ny` for all POIs and `ny_static` for just unflyable POIs.