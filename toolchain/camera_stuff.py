import cv2 as cv
import numpy as np
import glob
import os.path

class camera:
    mtx = None
    dist = None
    rvec = None
    tvec = None
    Hmat = None
    invHmat = None
    objp = None
    imgp = None
    objpts = None
    imgpts = None


    def __init__(self,width=1920,height=1080,cameraPort=0):
        self.width = width
        self.height = height
        self.cameraPort = cameraPort

        
        #self.vid = cv.VideoCapture(self.cameraPort,cv.CAP_DSHOW)
        #self.vid = cv.VideoCapture(self.cameraPort,cv.CAP_V4L)
        #self.vid = cv.VideoCapture(self.cameraPort)

        #self.vid.set(3,self.width)
        #self.vid.set(4,self.height)
        #self.vid.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        #self.vid.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)

    def set_resolution(self,width,height):
        self.width = width
        self.height = height

    def set_camera_port(self,cameraPort):
        self.cameraPort = cameraPort

    def start_camera(self):

        self.vid = cv.VideoCapture(self.cameraPort)
        self.vid.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
     

    def load_extrinsic_parameters(self,path):
        '''Loads intrinsic camera parameters rvec and tvec from a given path.'''
        # FILE_STORAGE_READ
        if os.path.isfile(path): 
            cv_file = cv.FileStorage(path, cv.FILE_STORAGE_READ)
            # note we also have to specify the type to retrieve other wise we only get a
            # FileNode object back instead of a matrix
            rvec = cv_file.getNode('rvec').mat()
            tvec = cv_file.getNode('tvec').mat()
            objp = cv_file.getNode('objp').mat()
            imgp = cv_file.getNode('imgp').mat()
            cv_file.release()

            self.rvec = rvec
            self.tvec = tvec
            self.objp = objp
            self.imgp = imgp
        else:
            print("Intrinsic camera parameters not found at path: " + path)


    def load_imagept(self,path):
        '''Loads intrinsic camera parameters rvec and tvec from a given path.'''
        # FILE_STORAGE_READ
        if os.path.isfile(path): 
            cv_file = cv.FileStorage(path, cv.FILE_STORAGE_READ)
            # note we also have to specify the type to retrieve other wise we only get a
            # FileNode object back instead of a matrix
            imgp = cv_file.getNode('imgp').mat()
            cv_file.release()

            self.imgp = imgp
        else:
            print("Imagepoints parameters not found at path: " + path)        

    def load_objectpts(self,path):
        '''load object points from file'''
        # FILE_STORAGE_READ
        if os.path.isfile(path): 
            cv_file = cv.FileStorage(path, cv.FILE_STORAGE_READ)
            # note we also have to specify the type to retrieve other wise we only get a
            # FileNode object back instead of a matrix
            objp = cv_file.getNode('objp').mat()
            cv_file.release()

            self.objp = objp
        else:
            print("Objectpoints parameters not found at path: " + path)   

    def transform_objectpts(self, scale, translation):
        '''transform object points'''
        self.objp = (self.objp + translation) * scale

    def mirror_objectpts(self, direction):
        '''mirror object points'''
        if direction == 'horizontal':
            self.objp[:, 0] = -self.objp[:, 0]
        elif direction == 'vertical':
            self.objp[:, 1] = -self.objp[:, 1]
        else:
            print("Invalid mirror direction. Please specify 'horizontal' or 'vertical'.")

    def rotate_objectpts(self, angle):
        '''rotate object points around the Z-axis'''
        # Convert angle from degrees to radians
        angle = angle * np.pi / 180
        # Create rotation matrix
        R_z = np.array([[np.cos(angle), -np.sin(angle), 0],
                        [np.sin(angle), np.cos(angle), 0],
                        [0, 0, 1]])
        # Rotate object points
        self.objp = self.objp @ R_z.T
  

    def store_extrinsic_parameters(self,path):
        '''Save the extrinsic camera Parameters rvec and tvec aswell as objp and imgp to given path/file.'''
        cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)
        cv_file.write('rvec', self.rvec)
        cv_file.write('tvec', self.tvec)
        cv_file.write('objp', self.objp)
        cv_file.write('imgp', self.imgp)
        cv_file.release()
        print('Extrinsic camera parameters rvec and tvec aswell as objp and imgp successfully saved')


    def load_intrinsic_parameters(self,path):
        '''Loads camera matrix and distortion coefficients.'''
   
        if os.path.isfile(path): 
            cv_file = cv.FileStorage(path, cv.FILE_STORAGE_READ)
            # note we also have to specify the type to retrieve other wise we only get a
            # FileNode object back instead of a matrix
            camera_matrix = cv_file.getNode('K').mat()
            dist_matrix = cv_file.getNode('D').mat()
            cv_file.release()
            self.mtx = camera_matrix
            self.dist = dist_matrix
        else:
            print("Intrinsic camera parameters not found at path: " + path)
                

    def store_intrinsic_parameters(self,path):
        '''Save the camera matrix and the distortion coefficients to given path/file.'''
        
        cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)
        cv_file.write('K', self.mtx)
        cv_file.write('D', self.dist)
        # note you *release* you don't close() a FileStorage object
        cv_file.release()
        print('Intrinsic camera parameters camera matrix and distortion coefficients successfully saved')


    def calc_extrinsic_parameters(self):
        #_,rvec,tvec = cv.solvePnP(self.objp,self.imgp,self.mtx,self.dist,None,None,None,cv.SOLVEPNP_IPPE)
        _,rvec,tvec = cv.solvePnP(self.objp,self.imgp,self.mtx,self.dist)

        self.rvec = rvec
        self.tvec = tvec


    def calc_intrinsic_parameters(self,marker_size,num_mark):
        
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


    def calc_homography(self):
        Hmat, _ =	cv.findHomography(self.objp, self.imgp)
        invHmat = np.linalg.inv(Hmat)

        self.Hmat = Hmat
        self.invHmat = invHmat


    def calc_images_object_points(self,images_path,num_chess_x,num_chess_y,edge_length):
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((num_chess_x*num_chess_y,3), np.float32)
        objp[:,:2] = np.mgrid[0:num_chess_x,0:num_chess_y].T.reshape(-1,2)
        objp = objp*edge_length
        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.

        # 'Data/*.jpg'
        images = glob.glob(images_path)
        for fname in images:
            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv.findChessboardCorners(gray, (num_chess_x,num_chess_y), None)
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners2)
        self.imgpts = imgpoints
        self.objpts = objpoints

            
    def calc_image_object_points(self,img,num_chess_x,num_chess_y,edge_length):
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((num_chess_x*num_chess_y,3), np.float32)
        objp[:,:2] = np.mgrid[0:num_chess_x,0:num_chess_y].T.reshape(-1,2)
        objp = objp*edge_length
        # Arrays to store object points and image points from all the images.
        
        imgpoints = [] # 2d points in image plane.

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (num_chess_x,num_chess_y), None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
            self.objp = objp
            self.imgp = corners2    
        else: 
            print('Error: No Chessboard detected')    


    def run_static(self):
        # vid = cv.VideoCapture(0)
        # vid.set(3,self.width)
        # vid.set(4,self.height)
        retval, img = self.vid.read()
        return img, retval


    def run_dynamic(self,num_chess_x,num_chess_y,edge_length):
        img,retval = self.run_static()
        if not retval:
            print('No image was taken')
        else:
            self.calc_image_object_points(img,num_chess_x,num_chess_y,edge_length)
            self.calc_homography()
            self.calc_extrinsic_parameters()
        return img, retval