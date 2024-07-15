import cv2 as cv
import numpy as np

class objectpoint:
    def __init__(self):
        self.obj_pts = np.array([])
        self.img = []
        self.counter = 0

    def add_points(self,object_pt):
        if self.obj_pts.size == 0:
            self.obj_pts = object_pt.reshape(1,len(object_pt))    
        else:
            self.obj_pts = np.vstack([self.obj_pts,object_pt])    
        self.counter += 1

    def delete_point(self):
        self.obj_pts = np.delete(self.obj_pts, -1, 0)
        self.counter -= 1

    def store_obj_pts(self,path):
        '''Save the extrinsic camera Parameters rvec and tvec aswell as objp and imgp to given path/file.'''
        cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)
        cv_file.write('imgp', self.obj_pts)
        cv_file.release()
        print('Imagepoints saved :' + path)