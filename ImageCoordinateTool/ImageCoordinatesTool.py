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
    #imagepath = 'backup_kalib/calibration02_img.jpg'
    

    # store object
    storage = objectpoint(imagepath)

    # displaying the image
    cv.imshow('image', storage.img[0])
 
    # setting mouse hadler for the image
    # and calling the click_event() function
    cv.setMouseCallback('image', click_event)
 
    # wait for a key to be pressed to exit
    cv.waitKey(0)
    

    # Print storage Array
    print(storage.obj_pts)
    
   
    now = datetime.now()
    d1 = now.strftime("_%Y_%m_%d_%H:%M")
    new_path_img = imagepath.replace(".jpg", d1 + ".jpg")
    new_path_data = imagepath.replace(".jpg", d1 + ".yml")
    cv.imwrite(new_path_img,storage.img[storage.counter])
    storage.store_obj_pts(new_path_data)
    # close the window
    cv.destroyAllWindows()