import utm
import geojson
import sys
import csv
from geojson import Feature, FeatureCollection, Point
import cv2 as cv
import numpy as np
from datetime import datetime

class objectpoint:
    def __init__(self):
        self.obj_pts = np.array([])
        self.counter = 0

    def add_points(self,object_pt):
        if self.obj_pts.size == 0:
            self.obj_pts = object_pt.reshape(1,3)
        else:
            self.obj_pts = np.vstack([self.obj_pts,object_pt])
        self.counter += 1

    def delete_point(self):
        self.obj_pts = np.delete(self.obj_pts, -1, 0)
        self.counter -= 1
        self.img.pop()

    def store_obj_pts(self,path):
        '''Save the points to given path/file.'''
        cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)
        cv_file.write('objp', self.obj_pts)
        cv_file.release()
        print('Objectpoints saved :' + path)





def convert_to_utm_coordinates_only(item):
    index, (longitude, latitude, altitude) = item
    easting, northing, zone_number, zone_letter = utm.from_latlon(latitude, longitude)
    return f"{easting:.02f} {northing:.02f} {altitude:.02f}"


def convert_to_utm(item):
    index, (longitude, latitude, altitude) = item
    easting, northing, zone_number, zone_letter = utm.from_latlon(latitude, longitude)
    return f"{index} {zone_number}{zone_letter} {easting:.02f} {northing:.02f} {altitude:.02f}"  
    #Diese Funktion gibt das Format wie folgt zurück:
    #zuerst den Index, dann das UTM Format, danach die Höhenmeter, jeweils mit Leerzeichen getrennt und auf zwei Nachkommastellen gerundet


coordinates = []
ref_features = []
ref_coordinates = []

print("Started Reading file")
if sys.argv[1].endswith('.geojson'):
    print("File is geoJSON")
    with open(sys.argv[1], "r") as read_file:
        print("Starting to convert json decoding")
        emps = geojson.load(read_file)
    for feature in emps['features']:
        coordinates.extend(geojson.utils.coords(feature))


if sys.argv[1].endswith('.csv'):
    print("File is csv")
    data_path = sys.argv[1]
    with open(sys.argv[1], "r") as csvfile:
        print("Starting to convert csv")

        lat_total = 0
        lon_total = 0
        elev_total = 0
        num_rows = 0
        features = []
        reader = csv.DictReader(csvfile, delimiter=',')
        #next(csvfile)
        for row in reader:
        # Name,Easting,Northing,Elevation,Description,Longitude,Latitude,Ellipsoidal height,Easting RMS,Northing RMS,Elevation RMS,Lateral RMS,Antenna height,Antenna height units,Solution status,Averaging start,Averaging end,Samples,PDOP,Base easting,Base northing,Base elevation,Base longitude,Base latitude,Base ellipsoidal height,Baseline,CS name
        #for Name,Easting,Northing,Elevation,Description,Longitude,Latitude,Ellipsoidal_height,Easting_RMS,Northing_RMS,Elevation_RMS,Lateral_RMS,Antenna_height,Antenna_height_units,Solution_status,Averaging_start,Averaging_end,Samples,PDOP,Base_easting,Base_northing,Base_elevation,Baseline in reader:
            Latitude, Longitude, Elevation = map(float, (row['Latitude'], row['Longitude'], row['Ellipsoidal height']))
            #print("Name: ", row['Name'])
            lat_total += Latitude
            lon_total += Longitude
            elev_total += Elevation
            num_rows += 1

            features.append(
                Feature(
                    geometry = Point((Longitude, Latitude, Elevation)), 
                    id = map(int, row['Name'])
                )
            )

    utm_coordinates = []
    for feature in features:
        # extract the latitude and longitude coordinates from the GeoJSON feature
        lon, lat, elev = feature["geometry"]["coordinates"]

        # convert the latitude and longitude coordinates to UTM coordinates
        easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)

        # add the UTM coordinates to the list
        utm_coordinates.append((easting, northing, zone_number, zone_letter, elev))


# Calculate the average values
lat_avg = lat_total / num_rows
lon_avg = lon_total / num_rows
elev_avg = elev_total / num_rows


center_easting, center_northing, center_zone_number, center_zone_letter =  utm.from_latlon(lat_avg, lon_avg)


local_coordinates = []
storage = objectpoint()

for coordinate in utm_coordinates:
    easting_local, northing_local, zone_number, zone_letter, elev_local = coordinate
    easting_local -= center_easting
    northing_local -= center_northing
    elev_local = 0.0
    # local_coordinates.append((easting_local, northing_local))
    local_coordinates.append((easting_local, northing_local, zone_number, zone_letter, elev_local))

    # Store coordinates in cv-File
    storage.add_points(np.array([easting_local,northing_local,elev_local]))
    print("Object points", storage.obj_pts)

# Print the average values
print('Average latitude:', lat_avg)
print('Average longitude:', lon_avg)
print('Average ellipsoidal elevation:', elev_avg)

center = (np.array([lat_avg,lon_avg,elev_avg]))

print('\n')
#print('\n'.join(map(convert_to_utm, enumerate(coordinates))))

#print(' '.join(map(convert_to_utm_coordinates_only, enumerate(coordinates))))
print(utm_coordinates)
print('\n')
print(center_easting, center_northing)
print('\n')
print(local_coordinates)
print('\n')
#print(obj_pts)

now = datetime.now()
d1 = now.strftime("_%Y-%m-%d_%H%M")
result_path = data_path.replace(".csv", "_obj_points" + d1 + ".yml")
center_path = data_path.replace(".csv", "_center" + d1 + ".yml")
cv_obj_point_file = cv.FileStorage(result_path, cv.FILE_STORAGE_WRITE)
cv_center_file = cv.FileStorage(center_path, cv.FILE_STORAGE_WRITE)
#all_obj_points = all_obj_points.reshape(-1,3)
cv_obj_point_file.write('objp', storage.obj_pts)
cv_center_file.write('center', center)
cv_center_file.release()
print(storage.obj_pts)
cv_obj_point_file.release()
print('Objectpoints saved :' + result_path)