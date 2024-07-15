from toolchain import camera_stuff
from postprocessing.projection_helper import *
import cv2
import numpy as np
import matplotlib.path as mpath
from shapely.geometry import Polygon, Point

class screen_display:
    def __init__(self, config_file):
        self.draw_axis = config_file.getboolean('Screen_Display', 'draw_axis')
        self.projected_image_width = config_file.getint('Screen_Display', 'projected_image_width')
        self.projected_image_height = config_file.getint('Screen_Display', 'projected_image_height')
        self.plot_x_min = config_file.getfloat('Screen_Display', 'plot_x_min')
        self.plot_x_max = config_file.getfloat('Screen_Display', 'plot_x_max')
        self.plot_y_min = config_file.getfloat('Screen_Display', 'plot_y_min')
        self.plot_y_max = config_file.getfloat('Screen_Display', 'plot_y_max')
        self.extent = [self.plot_x_min, self.plot_x_max, self.plot_y_min, self.plot_y_max]
        self.grid_resolution = config_file.getfloat('Screen_Display', 'grid_resolution')
        self.scale = self.projected_image_width / (self.plot_x_max - self.plot_x_min)
        assert (self.projected_image_height == self.projected_image_width)
        assert ((self.plot_y_max -self.plot_y_min) == (self.plot_x_max - self.plot_x_min))

class scene:
    def __init__(self,config_file):
        self.width = config_file.getint('Camera', 'width')
        self.height = config_file.getint('Camera', 'height')
        self.port = config_file.getint('Camera', 'port')

        self.intrinsic_path = config_file.get('Camera', 'intrinsic_path')
        self.img_pts_path = config_file.get('Camera', 'image_pts_path')
        self.obj_pts_path = config_file.get('Camera', 'object_pts_path')
        self.calibration_image = config_file.get('Camera', 'calibration_image_path')

        self.screen_display_setup = camera_stuff.camera(self.width, self.height, self.port)
        self.screen_display_setup.load_intrinsic_parameters(self.intrinsic_path)
        self.screen_display_setup.load_imagept(self.img_pts_path)

        self.real_camera_setup = camera_stuff.camera(self.width, self.height, self.port)
        self.real_camera_setup.load_intrinsic_parameters(self.intrinsic_path)
        self.real_camera_setup.load_imagept(self.img_pts_path)

    def calculate_camera_homography(self):
        self.real_camera_setup.load_objectpts(self.obj_pts_path)
        self.real_camera_setup.transform_objectpts(1.0, [0,0,0])
        self.real_camera_setup.calc_homography()

    def calculate_scene(self, display):
            translation = [-display.plot_x_min , display.plot_y_max, 0.0]
            #translation = [0.0 , 0.0, 0.0]
            self.screen_display_setup.load_objectpts(self.obj_pts_path)
            #self.screen_display_setup.mirror_objectpts('horizontal')
            #self.screen_display_setup.mirror_objectpts('vertical')
            self.screen_display_setup.transform_objectpts(display.scale, translation)
            self.screen_display_setup.calc_homography()
            self.image = cv2.imread(self.calibration_image)


            # Warp the image to the desired perspective using warpPerspective
            self.warped_image = cv2.warpPerspective(self.image, self.screen_display_setup.invHmat, (display.projected_image_width, display.projected_image_height))    
            self.warped_image = cv2.flip(self.warped_image, 0)
            print("x_min: {}, x_max: {}, y_min: {}, y_max: {}".format(*display.extent))

            self.warped_image = cv2.cvtColor(self.warped_image, cv2.COLOR_BGR2RGB)
            self.extent = display.extent

            #calculate a boundary polygon of the original image coordinates transformed to object points
            self.calculate_camera_homography()
            self.boundary = Polygon(self.get_boundary_polygon(self.width, self.height, self.extent))

    def draw_image_to_plot(self, axs, display):
            axs.imshow(self.warped_image, extent=display.extent)


    def binary_search(self, img_point_1, img_point_2):
        test_point= np.round((img_point_1 + img_point_2) / 2).astype(int)
        old_test_point = None
        while True:
        #do a binary search using the arithmetic mean of the two points
            if np.any(np.isinf(img2world(test_point, self.real_camera_setup.invHmat))) or np.any(np.isnan(img2world(test_point, self.real_camera_setup.invHmat))):
                print("Testpoint: ", test_point, "resulted in worldpoint: ", img2world(test_point, self.real_camera_setup.invHmat))
                img_point_1 = test_point
                print("img_point: ", img_point_1)
            else:
                world_point = img2world(test_point, self.real_camera_setup.invHmat)
                print("Testpoint: ", test_point, "resulted in worldpoint: ", img2world(test_point, self.real_camera_setup.invHmat))
                img_point_2 = test_point
                print("next_point: ", img_point_2)

            test_point = np.round((img_point_1 + img_point_2) / 2).astype(int)

            #Break if the test point is the same as the previous test point
            if np.array_equal(test_point, old_test_point):
                return world_point[0][:2]

            old_test_point = test_point



    def get_boundary_polygon(self, width, height, extent):
        offset = 20
        #boundary = np.array([[0,0],[width,0],[width,height],[0,height]])
        boundary = np.array([[0+offset,0+offset],[width-offset,0+offset],[width-offset,height-offset],[0+offset,height-offset]])
        #boundary = img2world(boundary, self.real_camera_setup.invHmat)
        #boundary = np.squeeze(boundary)
        # step through each point of boundary, if it a valid point, add it to a new list
        image_boundary = []
        for i in range(len(boundary)):
            img_point = boundary[i]
            world_point = img2world(boundary[i], self.real_camera_setup.invHmat)

            if np.any(np.isinf(world_point)) or np.any(np.isnan(world_point)):

                previous_point = boundary[(i - 1) % len(boundary)]
                if np.any(np.isinf(img2world(previous_point, self.real_camera_setup.invHmat))) or np.any(np.isnan(img2world(previous_point, self.real_camera_setup.invHmat))):
                    continue
                else:
                    binary_search_result = self.binary_search(img_point, previous_point)
                    image_boundary.append(binary_search_result)
                next_point = boundary[(i + 1) % len(boundary)]
                if np.any(np.isinf(img2world(next_point, self.real_camera_setup.invHmat))) or np.any(np.isnan(img2world(next_point, self.real_camera_setup.invHmat))):
                    continue
                else:
                    binary_search_result = self.binary_search(img_point, next_point)
                    image_boundary.append(binary_search_result) 
            else:
                image_boundary.append(world_point[0][:2])

        image_boundary = np.array(image_boundary)
        print("Image Boundary polygon: ", image_boundary)
        image_polygon = Polygon(image_boundary)
        extent_polygon = Polygon([(extent[0], extent[2]), (extent[1], extent[2]), (extent[1], extent[3]), (extent[0], extent[3])])
        boundary = image_polygon.intersection(extent_polygon)
        print("Extent Boundary polygon: ", np.array(boundary.exterior.coords))
        #print(boundary)
        return boundary

    def is_inside_polygon(self, point):
        return self.boundary.contains(Point(point['x'], point['y']))