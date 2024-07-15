# importing the module
import cv2 as cv
import numpy as np
from datetime import datetime
import argparse
import glob



# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
 
    # checking for left mouse clicks
    if event == cv.EVENT_LBUTTONDOWN:
        
        img = storage.img[storage.counter].copy()
     
        # displaying the coordinates
        # on the image window
        font = cv.FONT_HERSHEY_SIMPLEX
        out = cv.putText(img, str(storage.counter)+ ': '+ str(x) + ',' +
                    str(y), (x+5,y), font,
                    0.5, (255, 0, 0), 1)
                    
        #cv.drawKeypoints(img, [cv.KeyPoint(x,y,d)], img,(255, 0, 0)) 
        cv.drawMarker(img,(x,y),(255,0,0),cv.MARKER_TILTED_CROSS)
        
        # store x,y in store object
        storage.add_points(np.array([x,y]),img)

        cv.imshow('image', img)
        
        
 
    # checking for right mouse clicks    
    if event==cv.EVENT_RBUTTONDOWN:

        storage.delete_point()
        cv.imshow('image', storage.img[storage.counter])

                
    

class objectpoint:
    def __init__(self,imagepath):
        self.obj_pts = np.array([])
        self.img = []
        self.img.append(cv.imread(imagepath, 1))
        self.counter = 0

    def add_points(self,object_pt,img):
        if self.obj_pts.size == 0:
            self.obj_pts = object_pt.reshape(1,2)    
        else:
            self.obj_pts = np.vstack([self.obj_pts,object_pt])    
        self.counter += 1
        self.img.append(img)

    def delete_point(self):
        self.obj_pts = np.delete(self.obj_pts, -1, 0)
        self.counter -= 1
        self.img.pop()    

    def store_obj_pts(self,path):
        '''Save the extrinsic camera Parameters rvec and tvec aswell as objp and imgp to given path/file.'''
        cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)
        cv_file.write('imgp', self.obj_pts)
        cv_file.release()
        print('Imagepoints saved :' + path)


# driver function
if __name__=="__main__":
 
    
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", type=str, required=True,
        help="ImagePath")
    args = vars(ap.parse_args())

    imagepath = args["path"]

    all_obj_points = np.array([])
    
    data_path = ""

    print("Reading from file...\n")
    images = sorted(glob.glob(imagepath))
    for fname in images:
        # store object
        storage = objectpoint(fname)

        # displaying the image
        cv.imshow('image', storage.img[0])
    
        # setting mouse hadler for the image
        # and calling the click_event() function
        cv.setMouseCallback('image', click_event)
    
        # wait for a key to be pressed to exit
        cv.waitKey(0)
        

        # Print storage Array
        print(storage.obj_pts)
        all_obj_points = np.append(all_obj_points, storage.obj_pts) 

        now = datetime.now()
        d1 = now.strftime("_%Y-%m-%d_%H%M")
        new_path_img = fname.replace(".jpg", d1 + "_edit" + ".jpg")
        data_path = fname.replace(".jpg", d1 + ".yml")
        cv.imwrite(new_path_img,storage.img[storage.counter])
        cv.waitKey(10)
   
    now = datetime.now()
    d1 = now.strftime("_%Y-%m-%d_%H%M")
    # data_path = "image_points"
    # data_path = data_path + d1 + ".yml"
    cv_file = cv.FileStorage(data_path, cv.FILE_STORAGE_WRITE)
    all_obj_points = all_obj_points.reshape(-1,2)
    cv_file.write('imgp', all_obj_points)
    cv_file.release()
    print('Imagepoints saved :' + data_path)

    # storage.store_obj_pts(new_path_data)
    # close the window
    cv.destroyAllWindows()

