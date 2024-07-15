from toolchain import camera_stuff


import configparser
import argparse
from multiprocessing import Process, Queue
import time
import cv2 as cv
import numpy as np
import pickle
import socket
import json
from types import SimpleNamespace
import requests
import os
import numpy as np
import matplotlib.pyplot as plt


from toolchain import detector_stuff


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
                    "{:.2f}".format(point[1]), (int(point[0])+5,int(point[1])+offset), font,
                    0.5, (255, 0, 0), 1)
        cv.drawMarker(img,( int(point[0]), int(point[1]) ),(255,0,0),cv.MARKER_TILTED_CROSS)
        num_points += 1

def draw_imgandobj_points_to_image(img, points, prefix, offset = 0, obj_points = None):
    num_points = 0
    for point, obj_point in zip(points, obj_points):
        out = cv.putText(img, prefix + str(num_points)+ ': '+ "{:.2f}".format(point[0]) + ',' +
                    "{:.2f}".format(point[1]), (int(point[0])+5,int(point[1])+offset), font,
                    0.5, (255, 0, 0), 1)
        cv.putText(img,' obj: ' + "{:.2f}".format(obj_point[0]) + ',' +
                    "{:.2f}".format(obj_point[1]), (int(point[0])+5,int(point[1])+offset+20), font,
                    0.5, (255, 0, 0), 1)
        cv.drawMarker(img,( int(point[0]), int(point[1]) ),(255,0,0),cv.MARKER_TILTED_CROSS)
        num_points += 1

## Get argument 
if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", type=str, required=True,
        help="Path to config.ini data")
    args = vars(ap.parse_args())
    config_path = args["path"]

## Open config File
config_file = configparser.ConfigParser()
config_file.read(config_path)



# get config data from Camera
width = config_file.getint('Camera', 'width')
height = config_file.getint('Camera', 'height')
port = config_file.getint('Camera', 'port')

intrinsic_path = config_file.get('Camera', 'intrinsic_path')
img_pts_path = config_file.get('Camera', 'image_pts_path')
obj_pts_path = config_file.get('Camera', 'object_pts_path')

calibration_image_path = config_file.get('Camera', 'calibration_image_path')


brio = camera_stuff.camera(width,height,port)

# load image
calibration_image = cv.imread(calibration_image_path)
cv.imshow('calibration_image', calibration_image)
cv.waitKey(5)



## Function body
image_pts = []
brio.load_intrinsic_parameters(intrinsic_path)
# brio.load_imagept(img_pts_path)
# image_pts = brio.imgpts
if os.path.isfile(img_pts_path): 
    cv_file = cv.FileStorage(img_pts_path, cv.FILE_STORAGE_READ)
    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    image_pts = cv_file.getNode('imgp').mat()
    image_pts = image_pts.reshape(-1,2)
    # image_pts4 = image_pts[0:4].reshape(-1,2)
    cv_file.release()

image_pts = image_pts.astype(np.float64)

if os.path.isfile(obj_pts_path): 
    cv_file = cv.FileStorage(obj_pts_path, cv.FILE_STORAGE_READ)
    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    object_pts = cv_file.getNode('objp').mat()
    object_pts = object_pts.reshape(-1,3)
    cv_file.release()

object_pts = object_pts.astype(np.float64)


# Test data from c++ sample
# object_pts = np.array([[0., 0., 0.], [-511.,2181.,0.], [-3574.,2354.,0.], [-3400.,0.,0.]])
# image_pts = np.array([[271.,109.], [65.,208.], [334.,459.], [600.,225.]])


brio.objp = object_pts
brio.imgp = image_pts


brio.load_intrinsic_parameters(intrinsic_path)

brio.calc_homography()


H = cv.findHomography(object_pts, image_pts)
# P = cv.getPerspectiveTransform(object_pts, image_pts)#
# pts = np.float32(image_pts).reshape(-1,1,2)
# test = cv.perspectiveTransform(pts, H)

print ("Imagepoints: ", image_pts)
worldObjectPoints = img2world(image_pts, brio.invHmat)
print ("worldObjectPoints: ", worldObjectPoints)

imagePointsfromWorld = world2image(worldObjectPoints, brio.Hmat)
print ("Imagepoints from World Points: ", imagePointsfromWorld)

# 0: origin
line_image_pts = np.array([[ 1043., 314.], [840., 445.], [1162., 483.], [1454., 509. ]]) #[ 1043., 314.], [840., 445.], [1162., 483.,] [1454., 509. ][width/2 ,height/2], [1060., 734.], [1702., 766.]
# print ("new_image_pts", new_image_pts)
line_worldObjectPoints = img2world(line_image_pts, brio.invHmat)
new_worldObjectPoints = np.array([[0.0 ,0.0, 1.0], [5.0 ,0.0, 1.0], [0.0 ,5.0, 1.0]])

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

# for point in global_points:
#    plt.plot(point[0], point[1], 'ro')
#    plt.axis('scaled')
# plt.show()


image_calib_pts = world2image(global_points, brio.Hmat)

test_image_points_from_object_points = world2image(object_pts, brio.Hmat)
image_axis_points = world2image(new_worldObjectPoints, brio.Hmat)

# displaying the coordinates
# on the image window
font = cv.FONT_HERSHEY_SIMPLEX

draw_imgandobj_points_to_image(calibration_image, image_calib_pts, "K", 0, global_points)


#draw_points_to_image(calibration_image, new_image_pts, "",20)
draw_points_to_image(calibration_image, image_axis_points, "Axis",20)
draw_points_to_image(calibration_image, test_image_points_from_object_points, "T",40)
draw_imgandobj_points_to_image(calibration_image, image_pts, "I",60,object_pts)


cv.imshow('calibration_image', calibration_image)

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



# object_test = np.array([[6000.0,4000.0, 0], [0.0,4000.0, 0], [0.0,0.0, ], [6000.0,0.0, 0] ])

# object_test = np.array([[600.0,400.0, 0.0], [0.0,400.0, 0.0], [0.0,0.0, 0.0], [600.0,0.0, 0.0] ])
# image_test = np.array([[600.0,400.0], [0.0,400.0], [0.0,0.0], [600.0,0.0], ])
# image_test2 = np.array([[600.0,400.0, 1.0], [0.0,400.0, 1.0], [0.0,0.0, 1.0], [600.0,0.0, 1.0] ])

# shouldn't projected point yiels exactly the image points?
projected_point_test, jacobian = cv.projectPoints(object_pts, rvec, tvec, brio.mtx, brio.dist)
print ("projected_point_test: ", projected_point_test)


R , _ = cv.Rodrigues(rvec)
print ("Rodrigues: ",R)
# R_inv = np.zeros((3,3))
R_inv = np.linalg.inv(R)

point_test = np.array([1393., 737., 1.0])

mtx_inv = np.linalg.inv(brio.mtx)

LS = np.matmul(np.matmul(R_inv, mtx_inv), point_test)
print("LS:", LS)
RS = np.matmul(R_inv, tvec)
# RS = R_inv.dot(tvec_test)

print("RS: ",RS)
s = (0 + RS[2]) / LS[2]
# s = (285 + RS[2]) / LS[2]
print("s: ",s)


# point_src = np.array([[300.0,200.0]])

P0 = s* np.matmul(mtx_inv, point_test)
t_vec_neu = np.array([tvec[0][0], tvec[1][0], tvec[2][0]])
P1 = np.subtract(P0,t_vec_neu)
P =  np.matmul(R_inv, P1)
print("P: ",P)

cv.waitKey()
print("done")
cv.destroyAllWindows()

# projected_point, jacobian = cv.projectPoints(object_pts, rvec, tvec, brio.mtx, brio.dist)

# print ("projected_point: ",projected_point)