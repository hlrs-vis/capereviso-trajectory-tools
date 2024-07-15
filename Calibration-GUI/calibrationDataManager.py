import os
import cv2 as cv
import numpy as np
from toolchain import camera_stuff
from objectpoint import objectpoint
from objectpoint_coords import objectpoint_coords
import utm
import geojson
import csv
from geojson import Feature, Point
from datetime import datetime
import configparser

calibration_file = ""
image_file = ""
undistorted_image_file = ""
image_points_file = ""
original_coordinates_file = ""
utm_coordinates_file = ""
config_file = ""
check_image_file = ""
camera = camera_stuff.camera()
storage = objectpoint()

def set_image_file(filepath):
    global image_file
    image_file = filepath

def get_image_file():
    return image_file
    
def set_calibration_file(filepath):
    global calibration_file
    calibration_file = filepath

def get_calibration_file():
    return calibration_file
    
def set_undistorted_image_file(filepath):
    global undistorted_image_file
    undistorted_image_file = filepath

def get_undistorted_image_file():
    return undistorted_image_file

def set_image_points_file(filepath):
    global image_points_file
    image_points_file = filepath

def get_image_points_file():
    return image_points_file

def set_original_coordinates_file(filepath):
    global original_coordinates_file
    original_coordinates_file = filepath

def get_original_coordinates_file():
    return original_coordinates_file

def set_utm_coordinates_file(filepath):
    global utm_coordinates_file
    utm_coordinates_file = filepath

def get_utm_coordinates_file():
    return utm_coordinates_file

def set_config_file(filepath):
    global config_file
    config_file = filepath

def get_config_file():
    return config_file

def set_check_image_file(filepath):
    global check_image_file
    check_image_file = filepath

def get_check_image_file():
    return check_image_file

def undistort_image():
    global undistorted_image_file
    global storage
    camera.set_resolution(1920,1080)
    camera.load_intrinsic_parameters(calibration_file)
    image = cv.imread(image_file)
    unimg = cv.undistort(image, camera.mtx, camera.dist)
    undistorted_image_file = image_file.replace(".jpg", "_undistorted.jpg")
    cv.imwrite(undistorted_image_file, unimg)

def add_point(object_point):
    storage.add_points(object_point)

def convert_to_opencv():
    global original_coordinates_file
    global utm_coordinates_file

    coordinates = []
    ref_features = []
    ref_coordinates = []

    print("Started Reading file")
    if original_coordinates_file.endswith('.geojson'):
        print("File is geoJSON")
        with open(original_coordinates_file, "r") as read_file:
            print("Starting to convert json decoding")
            emps = geojson.load(read_file)
        for feature in emps['features']:
            coordinates.extend(geojson.utils.coords(feature))


    if original_coordinates_file.endswith('.csv'):
        print("File is csv")
        data_path = original_coordinates_file
        with open(original_coordinates_file, "r") as csvfile:
            print("Starting to convert csv")

            lat_total = 0
            lon_total = 0
            elev_total = 0
            num_rows = 0
            features = []
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
            # Name,Easting,Northing,Elevation,Description,Longitude,Latitude,Ellipsoidal height,Easting RMS,Northing RMS,Elevation RMS,Lateral RMS,Antenna height,Antenna height units,Solution status,Averaging start,Averaging end,Samples,PDOP,Base easting,Base northing,Base elevation,Base longitude,Base latitude,Base ellipsoidal height,Baseline,CS name
            #for Name,Easting,Northing,Elevation,Description,Longitude,Latitude,Ellipsoidal_height,Easting_RMS,Northing_RMS,Elevation_RMS,Lateral_RMS,Antenna_height,Antenna_height_units,Solution_status,Averaging_start,Averaging_end,Samples,PDOP,Base_easting,Base_northing,Base_elevation,Baseline in reader:
                Latitude, Longitude, Elevation = map(float, (row['Latitude'], row['Longitude'], row['Ellipsoidal height']))
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

    lat_avg = lat_total / num_rows
    lon_avg = lon_total / num_rows
    elev_avg = elev_total / num_rows

    center_easting, center_northing, center_zone_number, center_zone_letter =  utm.from_latlon(lat_avg, lon_avg)

    local_coordinates = []
    storage = objectpoint_coords()

    for coordinate in utm_coordinates:
        easting_local, northing_local, zone_number, zone_letter, elev_local = coordinate
        easting_local -= center_easting
        northing_local -= center_northing
        easting_local -= 1000 * easting_local
        northing_local -= 1000 * northing_local
        elev_local = 0.0
        local_coordinates.append((easting_local, northing_local, zone_number, zone_letter, elev_local))

        storage.add_points(np.array([easting_local,northing_local,elev_local]))
        print("Object points", storage.obj_pts)

    print('Average latitude:', lat_avg)
    print('Average longitude:', lon_avg)
    print('Average ellipsoidal elevation:', elev_avg)
    print('\n')
    print(utm_coordinates)
    print('\n')
    print(center_easting, center_northing)
    print('\n')
    print(local_coordinates)
    print('\n')

    now = datetime.now()
    d1 = now.strftime("_%Y-%m-%d_%H%M")
    data_path = data_path.replace(".csv", "_obj_points" + d1 + ".yml")
    cv_file = cv.FileStorage(data_path, cv.FILE_STORAGE_WRITE)
    cv_file.write('objp', storage.obj_pts)
    set_utm_coordinates_file(data_path)
    print(storage.obj_pts)
    cv_file.release()
    print('Imagepoints saved :' + data_path)

def updateConfig(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    config['Camera']['image_pts_path'] = image_points_file
    config['Camera']['object_pts_path'] = utm_coordinates_file
    config['Camera']['calibration_image_path'] = undistorted_image_file
    with open(filename, 'w') as configfile:
        config.write(configfile)
    print("gepeichert als" + str(filename))

def saveStorageToFile():
    global undistorted_image_file
    global storage
    global image_points_file

    now = datetime.now()
    d1 = now.strftime("_%Y-%m-%d_%H%M")
    data_path = undistorted_image_file.replace(".jpg", d1 + ".yml")
    cv_file = cv.FileStorage(data_path, cv.FILE_STORAGE_WRITE)
    all_obj_points = storage.obj_pts.reshape(-1,2)
    cv_file.write('imgp', all_obj_points)
    cv_file.release()
    image_points_file = data_path
    print('Imagepoints saved :' + data_path)

def img2world(image_points,invHmat):
    all_world_points = np.array([])
    for image_pt in image_points:
        ip = np.append(image_pt.reshape(1,2),1)
        world_points = np.matmul(invHmat,ip)
        world_points[0] = world_points[0]/world_points[2]
        world_points[1] = world_points[1]/world_points[2]
        world_points[2] = world_points[2]/world_points[2]
        all_world_points = np.append(all_world_points, world_points.reshape(1,3)[0:2])
    all_world_points = all_world_points.reshape(-1,3)
    return all_world_points


def world2image(world_points,Hmat):
    all_image_points = np.array([])
    for world_pt in world_points:
        wp = np.append(world_pt[0:2].reshape(1,2),1)
        image_points = np.matmul(Hmat,wp)
        image_points[0] = image_points[0]/image_points[2]
        image_points[1] = image_points[1]/image_points[2]
        image_points[2] = image_points[2]/image_points[2]
        all_image_points = np.append(all_image_points, image_points[0:2].reshape(1,2))
    all_image_points = all_image_points.reshape(-1,2)
    return all_image_points


def make_rot(angle):
    cost = np.cos(np.deg2rad(angle))
    sint = np.sin(np.deg2rad(angle))
    rot = np.array([[cost, -sint, 0],
                   [sint, cost, 0],
                   [0, 0, 1]])
    return rot

def draw_points_to_image(img, points, prefix, offset = 0):
    num_points = 0
    for point in points:
        out = cv.putText(img, prefix + str(num_points)+ ': '+ "{:.2f}".format(point[0]) + ',' +
                    "{:.2f}".format(point[1]), (int(point[0])+5,int(point[1])+offset), cv.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 0, 0), 1)
        cv.drawMarker(img,( int(point[0]), int(point[1]) ),(255,0,0),cv.MARKER_TILTED_CROSS)
        num_points += 1

def check_calibration():
    global check_image_file
    global config_file

    config_path = config_file

    config_file = configparser.ConfigParser()
    config_file.read(config_path)

    width = config_file.getint('Camera', 'width')
    height = config_file.getint('Camera', 'height')
    port = config_file.getint('Camera', 'port')

    intrinsic_path = config_file.get('Camera', 'intrinsic_path')
    img_pts_path = config_file.get('Camera', 'image_pts_path')
    obj_pts_path = config_file.get('Camera', 'object_pts_path')

    calibration_image_path = config_file.get('Camera', 'calibration_image_path')

    brio = camera_stuff.camera(width,height,port)

    calibration_image = cv.imread(calibration_image_path)

    image_pts = []
    brio.load_intrinsic_parameters(intrinsic_path)
    if os.path.isfile(img_pts_path): 
        cv_file = cv.FileStorage(img_pts_path, cv.FILE_STORAGE_READ)
        image_pts = cv_file.getNode('imgp').mat()
        image_pts = image_pts.reshape(-1,2)
        cv_file.release()

    image_pts = image_pts.astype(np.float64)

    if os.path.isfile(obj_pts_path): 
        cv_file = cv.FileStorage(obj_pts_path, cv.FILE_STORAGE_READ)
        object_pts = cv_file.getNode('objp').mat()
        object_pts = object_pts.reshape(-1,3)
        cv_file.release()

    object_pts = object_pts.astype(np.float64)
    brio.objp = object_pts
    brio.imgp = image_pts

    brio.load_intrinsic_parameters(intrinsic_path)

    brio.calc_homography()

    H = cv.findHomography(object_pts, image_pts)

    print ("Imagepoints: ", image_pts)
    worldObjectPoints = img2world(image_pts, brio.invHmat)
    print ("worldObjectPoints: ", worldObjectPoints)

    imagePointsfromWorld = world2image(worldObjectPoints, brio.Hmat)
    print ("Imagepoints from World Points: ", imagePointsfromWorld)

    line_image_pts = np.array([[ 1043., 314.], [840., 445.], [1162., 483.], [1454., 509. ]]) #[ 1043., 314.], [840., 445.], [1162., 483.,] [1454., 509. ][width/2 ,height/2], [1060., 734.], [1702., 766.]
    line_worldObjectPoints = img2world(line_image_pts, brio.invHmat)
    new_worldObjectPoints = np.array([[0.0 ,0.0, 1.0], [5000.0 ,0.0, 1.0], [0.0 ,5000.0, 1.0]])

    print("line_worldObjectPoints",line_worldObjectPoints)

    print("new_worldObjectPoints",new_worldObjectPoints)
    x_axis = new_worldObjectPoints[1]-new_worldObjectPoints[2]
    x_axis1 = 5000*x_axis/np.linalg.norm(x_axis)

    B0 = np.array([0.0, 0.0])

    global_points = np.array([])

    K0 = new_worldObjectPoints[0]
    rotation3D = make_rot(90)
    K1 = K0 + x_axis1
    K2 = K0 - x_axis1
    y_axis = np.matmul(rotation3D, x_axis1)
    K3 = K0 + y_axis
    K4 = K0 - y_axis
    global_points = np.append(global_points, (K0, K1, K2, K3, K4))
    global_points = global_points.reshape(-1,3)

    image_calib_pts = world2image(global_points, brio.Hmat)

    test_image_points_from_object_points = world2image(object_pts, brio.Hmat)
    image_axis_points = world2image(new_worldObjectPoints, brio.Hmat)

    draw_points_to_image(calibration_image, image_calib_pts, "K")

    draw_points_to_image(calibration_image, image_axis_points, "Axis",20)
    draw_points_to_image(calibration_image, test_image_points_from_object_points, "T",40)
    draw_points_to_image(calibration_image, image_pts, "I",60)

    file_path = "Kalibrationscheck.jpg"
    set_check_image_file(file_path)
    cv.imwrite(get_check_image_file(), calibration_image)

    print("K0:", K0) # 0.0, 0.0
    print("K1:", K1) # 1.0, 0.0
    print("K2:", K2) # -1.0, 0.0
    print("K3:", K3) # 0.0, 1.0
    print("K4:", K4) # 0.0, -1.0

    print("cross", np.cross(K1-K0, K3-K0))

    print(object_pts.shape[0])
    print(image_pts.shape[0])
    assert object_pts.shape[0] == image_pts.shape[0]
    (_, rvec, tvec ) = cv.solvePnP(object_pts, image_pts, brio.mtx, brio.dist)

    projected_point_test, jacobian = cv.projectPoints(object_pts, rvec, tvec, brio.mtx, brio.dist)
    print ("projected_point_test: ", projected_point_test)

    R , _ = cv.Rodrigues(rvec)
    print ("Rodrigues: ",R)
    R_inv = np.linalg.inv(R)

    point_test = np.array([1393., 737., 1.0])

    mtx_inv = np.linalg.inv(brio.mtx)

    LS = np.matmul(np.matmul(R_inv, mtx_inv), point_test)
    print("LS:", LS)
    RS = np.matmul(R_inv, tvec)

    print("RS: ",RS)
    s = (0 + RS[2]) / LS[2]
    print("s: ",s)

    P0 = s* np.matmul(mtx_inv, point_test)
    t_vec_neu = np.array([tvec[0][0], tvec[1][0], tvec[2][0]])
    P1 = np.subtract(P0,t_vec_neu)
    P =  np.matmul(R_inv, P1)
    print("P: ",P)

    print("done")